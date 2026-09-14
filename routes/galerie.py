from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import PhotoGalerie
from utils import traiter_photo

galerie_bp = Blueprint("galerie", __name__, url_prefix="/galerie")


@galerie_bp.route("/")
@login_required
def index():
    photos = PhotoGalerie.query.order_by(PhotoGalerie.date_ajout.desc()).all()
    return render_template("galerie/index.html", photos=photos)


@galerie_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()

        photo_data, erreur = traiter_photo(request.files.get("photo"))
        if not photo_data:
            flash(erreur or "Merci de choisir une photo.", "error")
            return render_template("galerie/ajouter.html")

        photo = PhotoGalerie(
            titre=titre or None,
            description=description or None,
            photo_data=photo_data,
            proprietaire_id=current_user.id,
        )
        db.session.add(photo)
        db.session.commit()
        flash("Photo ajoutée à la galerie.", "success")
        return redirect(url_for("galerie.index"))

    return render_template("galerie/ajouter.html")


@galerie_bp.route("/<int:photo_id>/supprimer", methods=["POST"])
@login_required
def supprimer(photo_id):
    photo = PhotoGalerie.query.filter_by(
        id=photo_id, proprietaire_id=current_user.id
    ).first()
    if photo is None:
        abort(404)

    db.session.delete(photo)
    db.session.commit()
    flash("Photo supprimée.", "info")
    return redirect(url_for("galerie.index"))