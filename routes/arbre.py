from flask import Blueprint, render_template
from flask_login import login_required

from models import FamilyMember

arbre_bp = Blueprint("arbre", __name__)


@arbre_bp.route("/arbre")
@login_required
def arbre():
    # Un "foyer" par membre inscrit (profil utilisateur), avec ses parents s'il en a renseigné
    foyers = FamilyMember.query.filter_by(est_soi=True).order_by(FamilyMember.nom).all()
    return render_template("arbre.html", foyers=foyers)