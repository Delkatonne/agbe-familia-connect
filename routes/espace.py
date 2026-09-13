from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import FamilyMember, ChampPersonnalise
from utils import traiter_photo

espace_bp = Blueprint("espace", __name__, url_prefix="/mon-espace")


def _parse_date(valeur):
    if not valeur:
        return None
    try:
        return datetime.strptime(valeur, "%Y-%m-%d").date()
    except ValueError:
        return None


def _recalculer_liens_parents(mon_profil, user_id):
    """Met à jour pere_id/mere_id sur le profil de l'utilisateur, à partir
    des parents qu'il a ajoutés — utilisé pour construire l'arbre généalogique."""
    if not mon_profil:
        return
    pere = FamilyMember.query.filter_by(
        proprietaire_id=user_id, est_soi=False, lien_parente="Père"
    ).first()
    mere = FamilyMember.query.filter_by(
        proprietaire_id=user_id, est_soi=False, lien_parente="Mère"
    ).first()
    mon_profil.pere_id = pere.id if pere else None
    mon_profil.mere_id = mere.id if mere else None


@espace_bp.route("/")
@login_required
def index():
    mon_profil = FamilyMember.query.filter_by(
        proprietaire_id=current_user.id, est_soi=True
    ).first()
    parents = FamilyMember.query.filter_by(
        proprietaire_id=current_user.id, est_soi=False
    ).all()
    return render_template("espace/index.html", mon_profil=mon_profil, parents=parents)


@espace_bp.route("/modifier", methods=["GET", "POST"])
@login_required
def modifier_profil():
    mon_profil = FamilyMember.query.filter_by(
        proprietaire_id=current_user.id, est_soi=True
    ).first()

    if request.method == "POST":
        nom_profil = request.form.get("nom_profil", "").strip()
        date_naissance = _parse_date(request.form.get("date_naissance"))
        profession = request.form.get("profession", "").strip()
        telephone = request.form.get("telephone", "").strip()
        biographie = request.form.get("biographie", "").strip()

        if not nom_profil:
            flash("Le nom de profil est obligatoire.", "error")
            return render_template("espace/modifier_profil.html", mon_profil=mon_profil)

        photo_data, erreur_photo = traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/modifier_profil.html", mon_profil=mon_profil)

        current_user.nom_profil = nom_profil
        current_user.date_naissance = date_naissance
        current_user.profession = profession
        current_user.telephone = telephone

        if mon_profil:
            mon_profil.nom = nom_profil
            mon_profil.date_naissance = date_naissance
            mon_profil.profession = profession
            mon_profil.telephone = telephone
            mon_profil.biographie = biographie
            if photo_data:
                mon_profil.photo_data = photo_data
        else:
            mon_profil = FamilyMember(
                nom=nom_profil,
                date_naissance=date_naissance,
                profession=profession,
                telephone=telephone,
                biographie=biographie,
                photo_data=photo_data,
                est_soi=True,
                proprietaire_id=current_user.id,
            )
            db.session.add(mon_profil)

        db.session.commit()
        flash("Vos informations ont été mises à jour.", "success")
        return redirect(url_for("espace.index"))

    return render_template("espace/modifier_profil.html", mon_profil=mon_profil)


@espace_bp.route("/parents/ajouter", methods=["GET", "POST"])
@login_required
def ajouter_parent():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        lien_parente = request.form.get("lien_parente", "").strip()
        date_naissance = _parse_date(request.form.get("date_naissance"))
        profession = request.form.get("profession", "").strip()
        telephone = request.form.get("telephone", "").strip()
        biographie = request.form.get("biographie", "").strip()

        if not nom:
            flash("Le nom est obligatoire.", "error")
            return render_template("espace/parent_form.html", parent=None)

        photo_data, erreur_photo = traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/parent_form.html", parent=None)

        parent = FamilyMember(
            nom=nom,
            lien_parente=lien_parente,
            date_naissance=date_naissance,
            profession=profession,
            telephone=telephone,
            biographie=biographie,
            photo_data=photo_data,
            est_soi=False,
            proprietaire_id=current_user.id,
        )
        db.session.add(parent)
        db.session.flush()

        mon_profil = FamilyMember.query.filter_by(
            proprietaire_id=current_user.id, est_soi=True
        ).first()
        _recalculer_liens_parents(mon_profil, current_user.id)

        db.session.commit()
        flash("Parent ajouté.", "success")
        return redirect(url_for("espace.index"))

    return render_template("espace/parent_form.html", parent=None)


@espace_bp.route("/parents/<int:parent_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier_parent(parent_id):
    parent = FamilyMember.query.filter_by(
        id=parent_id, proprietaire_id=current_user.id, est_soi=False
    ).first()
    if parent is None:
        abort(404)

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        if not nom:
            flash("Le nom est obligatoire.", "error")
            return render_template("espace/parent_form.html", parent=parent)

        photo_data, erreur_photo = traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/parent_form.html", parent=parent)

        parent.nom = nom
        parent.lien_parente = request.form.get("lien_parente", "").strip()
        parent.date_naissance = _parse_date(request.form.get("date_naissance"))
        parent.profession = request.form.get("profession", "").strip()
        parent.telephone = request.form.get("telephone", "").strip()
        parent.biographie = request.form.get("biographie", "").strip()
        if photo_data:
            parent.photo_data = photo_data

        mon_profil = FamilyMember.query.filter_by(
            proprietaire_id=current_user.id, est_soi=True
        ).first()
        _recalculer_liens_parents(mon_profil, current_user.id)

        db.session.commit()
        flash("Informations mises à jour.", "success")
        return redirect(url_for("espace.index"))

    return render_template("espace/parent_form.html", parent=parent)


@espace_bp.route("/parents/<int:parent_id>/supprimer", methods=["POST"])
@login_required
def supprimer_parent(parent_id):
    parent = FamilyMember.query.filter_by(
        id=parent_id, proprietaire_id=current_user.id, est_soi=False
    ).first()
    if parent is None:
        abort(404)

    db.session.delete(parent)
    db.session.flush()

    mon_profil = FamilyMember.query.filter_by(
        proprietaire_id=current_user.id, est_soi=True
    ).first()
    _recalculer_liens_parents(mon_profil, current_user.id)

    db.session.commit()
    flash("Le parent a été supprimé.", "info")
    return redirect(url_for("espace.index"))


@espace_bp.route("/<int:membre_id>/champs/ajouter", methods=["POST"])
@login_required
def ajouter_champ(membre_id):
    membre = FamilyMember.query.filter_by(
        id=membre_id, proprietaire_id=current_user.id
    ).first()
    if membre is None:
        abort(404)

    titre = request.form.get("titre", "").strip()
    valeur = request.form.get("valeur", "").strip()

    if not titre or not valeur:
        flash("Le titre et la valeur sont obligatoires.", "error")
        return redirect(url_for("espace.index"))

    champ = ChampPersonnalise(family_member_id=membre.id, titre=titre, valeur=valeur)
    db.session.add(champ)
    db.session.commit()
    flash("Information ajoutée.", "success")
    return redirect(url_for("espace.index"))


@espace_bp.route("/champs/<int:champ_id>/supprimer", methods=["POST"])
@login_required
def supprimer_champ(champ_id):
    champ = (
        ChampPersonnalise.query.join(FamilyMember)
        .filter(
            ChampPersonnalise.id == champ_id,
            FamilyMember.proprietaire_id == current_user.id,
        )
        .first()
    )
    if champ is None:
        abort(404)

    db.session.delete(champ)
    db.session.commit()
    flash("Information supprimée.", "info")
    return redirect(url_for("espace.index"))