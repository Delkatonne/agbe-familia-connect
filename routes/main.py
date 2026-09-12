from flask import Blueprint, render_template
from flask_login import login_required

from models import FamilyMember, Event, HeritageItem

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def accueil():
    return render_template("index.html")


@main_bp.route("/famille")
@login_required
def famille():
    membres = FamilyMember.query.order_by(FamilyMember.date_naissance).all()
    return render_template("famille.html", membres=membres)


@main_bp.route("/histoire")
@login_required
def histoire():
    return render_template("histoire.html")


@main_bp.route("/patrimoine")
@login_required
def patrimoine():
    elements = HeritageItem.query.all()
    return render_template("patrimoine.html", elements=elements)


@main_bp.route("/evenements")
@login_required
def evenements():
    evenements = Event.query.order_by(Event.date_evenement).all()
    return render_template("evenements.html", evenements=evenements)
