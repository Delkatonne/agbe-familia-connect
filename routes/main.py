from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import FamilyMember, Event, HeritageItem, Publication
from utils import traiter_photo

main_bp = Blueprint("main", __name__)


def _parse_date(valeur):
    if not valeur:
        return None
    try:
        return datetime.strptime(valeur, "%Y-%m-%d").date()
    except ValueError:
        return None


@main_bp.route("/")
def accueil():
    return render_template("index.html")


@main_bp.route("/famille")
@login_required
def famille():
    membres = FamilyMember.query.order_by(FamilyMember.date_naissance).all()
    return render_template("famille.html", membres=membres)


@main_bp.route("/famille/<int:membre_id>")
@login_required
def profil_membre(membre_id):
    membre = FamilyMember.query.get_or_404(membre_id)
    est_mon_profil = (
        membre.est_soi
        and membre.proprietaire_id is not None
        and membre.proprietaire_id == current_user.id
    )
    peut_envoyer_message = (
        membre.est_soi
        and membre.proprietaire_id is not None
        and membre.proprietaire_id != current_user.id
    )
    return render_template(
        "profil_membre.html",
        membre=membre,
        est_mon_profil=est_mon_profil,
        peut_envoyer_message=peut_envoyer_message,
    )


@main_bp.route("/famille/<int:membre_id>/publications/ajouter", methods=["POST"])
@login_required
def ajouter_publication(membre_id):
    membre = FamilyMember.query.get_or_404(membre_id)

    if not (membre.est_soi and membre.proprietaire_id == current_user.id):
        abort(403)

    contenu = request.form.get("contenu", "").strip()
    if not contenu:
        flash("Le message ne peut pas être vide.", "error")
        return redirect(url_for("main.profil_membre", membre_id=membre_id))

    photo_data, erreur_photo = traiter_photo(request.files.get("photo"))
    if erreur_photo:
        flash(erreur_photo, "error")
        return redirect(url_for("main.profil_membre", membre_id=membre_id))

    publication = Publication(
        family_member_id=membre.id,
        auteur_id=current_user.id,
        contenu=contenu,
        photo_data=photo_data,
    )
    db.session.add(publication)
    db.session.commit()
    flash("Publication ajoutée.", "success")
    return redirect(url_for("main.profil_membre", membre_id=membre_id))


@main_bp.route("/publications/<int:publication_id>/supprimer", methods=["POST"])
@login_required
def supprimer_publication(publication_id):
    publication = Publication.query.get_or_404(publication_id)
    if publication.auteur_id != current_user.id:
        abort(403)

    membre_id = publication.family_member_id
    db.session.delete(publication)
    db.session.commit()
    flash("Publication supprimée.", "info")
    return redirect(url_for("main.profil_membre", membre_id=membre_id))


@main_bp.route("/histoire")
@login_required
def histoire():
    return render_template("histoire.html")


@main_bp.route("/patrimoine")
@login_required
def patrimoine():
    elements = HeritageItem.query.order_by(HeritageItem.id.desc()).all()
    return render_template("patrimoine.html", elements=elements)


@main_bp.route("/patrimoine/ajouter", methods=["GET", "POST"])
@login_required
def ajouter_patrimoine():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()

        if not titre:
            flash("Le titre est obligatoire.", "error")
            return render_template("patrimoine_form.html")

        photo_data, erreur_photo = traiter_photo(request.files.get("photo"))
        if erreur_photo:
            flash(erreur_photo, "error")
            return render_template("patrimoine_form.html")

        element = HeritageItem(
            titre=titre,
            description=description,
            photo_data=photo_data,
            proprietaire_id=current_user.id,
        )
        db.session.add(element)
        db.session.commit()
        flash("Élément ajouté au patrimoine.", "success")
        return redirect(url_for("main.patrimoine"))

    return render_template("patrimoine_form.html")


@main_bp.route("/patrimoine/<int:element_id>/supprimer", methods=["POST"])
@login_required
def supprimer_patrimoine(element_id):
    element = HeritageItem.query.get_or_404(element_id)
    if element.proprietaire_id != current_user.id:
        abort(403)

    db.session.delete(element)
    db.session.commit()
    flash("Élément supprimé.", "info")
    return redirect(url_for("main.patrimoine"))


@main_bp.route("/evenements")
@login_required
def evenements():
    evenements = Event.query.order_by(Event.date_evenement).all()
    return render_template("evenements.html", evenements=evenements)


@main_bp.route("/evenements/ajouter", methods=["GET", "POST"])
@login_required
def ajouter_evenement():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        date_evenement = _parse_date(request.form.get("date_evenement"))
        lieu = request.form.get("lieu", "").strip()

        if not titre or not date_evenement:
            flash("Le titre et la date sont obligatoires.", "error")
            return render_template("evenement_form.html")

        evenement = Event(
            titre=titre,
            description=description,
            date_evenement=date_evenement,
            lieu=lieu,
            proprietaire_id=current_user.id,
        )
        db.session.add(evenement)
        db.session.commit()
        flash("Événement ajouté.", "success")
        return redirect(url_for("main.evenements"))

    return render_template("evenement_form.html")


@main_bp.route("/evenements/<int:evenement_id>/supprimer", methods=["POST"])
@login_required
def supprimer_evenement(evenement_id):
    evenement = Event.query.get_or_404(evenement_id)
    if evenement.proprietaire_id != current_user.id:
        abort(403)

    db.session.delete(evenement)
    db.session.commit()
    flash("Événement supprimé.", "info")
    return redirect(url_for("main.evenements"))