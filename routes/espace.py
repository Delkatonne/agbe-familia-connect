import base64
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import FamilyMember

espace_bp = Blueprint("espace", __name__, url_prefix="/mon-espace")

TYPES_IMAGE_AUTORISES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAILLE_IMAGE_MAX = 2 * 1024 * 1024  # 2 Mo


def _parse_date(valeur):
    if not valeur:
        return None
    try:
        return datetime.strptime(valeur, "%Y-%m-%d").date()
    except ValueError:
        return None


def _traiter_photo(fichier):
    """
    Retourne (photo_data, erreur).
    - photo_data est None si aucun fichier n'a été fourni (on garde l'ancienne photo).
    - erreur est une chaîne à afficher si le fichier fourni est invalide.
    """
    if not fichier or not fichier.filename:
        return None, None

    if fichier.mimetype not in TYPES_IMAGE_AUTORISES:
        return None, "Format d'image non supporté (JPEG, PNG, WEBP ou GIF uniquement)."

    contenu = fichier.read()
    if len(contenu) > TAILLE_IMAGE_MAX:
        return None, "L'image dépasse la taille maximale autorisée (2 Mo)."

    encode = base64.b64encode(contenu).decode("utf-8")
    return f"data:{fichier.mimetype};base64,{encode}", None


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
        biographie = request.form.get("biographie", "").strip()

        if not nom_profil:
            flash("Le nom de profil est obligatoire.", "error")
            return render_template("espace/modifier_profil.html", mon_profil=mon_profil)

        photo_data, erreur_photo = _traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/modifier_profil.html", mon_profil=mon_profil)

        current_user.nom_profil = nom_profil
        current_user.date_naissance = date_naissance
        current_user.profession = profession

        if mon_profil:
            mon_profil.nom = nom_profil
            mon_profil.date_naissance = date_naissance
            mon_profil.profession = profession
            mon_profil.biographie = biographie
            if photo_data:
                mon_profil.photo_data = photo_data
        else:
            mon_profil = FamilyMember(
                nom=nom_profil,
                date_naissance=date_naissance,
                profession=profession,
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
        biographie = request.form.get("biographie", "").strip()

        if not nom:
            flash("Le nom est obligatoire.", "error")
            return render_template("espace/parent_form.html", parent=None)

        photo_data, erreur_photo = _traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/parent_form.html", parent=None)

        parent = FamilyMember(
            nom=nom,
            lien_parente=lien_parente,
            date_naissance=date_naissance,
            profession=profession,
            biographie=biographie,
            photo_data=photo_data,
            est_soi=False,
            proprietaire_id=current_user.id,
        )
        db.session.add(parent)
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

        photo_data, erreur_photo = _traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("espace/parent_form.html", parent=parent)

        parent.nom = nom
        parent.lien_parente = request.form.get("lien_parente", "").strip()
        parent.date_naissance = _parse_date(request.form.get("date_naissance"))
        parent.profession = request.form.get("profession", "").strip()
        parent.biographie = request.form.get("biographie", "").strip()
        if photo_data:
            parent.photo_data = photo_data

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
    db.session.commit()
    flash("Le parent a été supprimé.", "info")
    return redirect(url_for("espace.index"))