from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, FamilyMember

auth_bp = Blueprint("auth", __name__)


def _parse_date(valeur):
    if not valeur:
        return None
    try:
        return datetime.strptime(valeur, "%Y-%m-%d").date()
    except ValueError:
        return None


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("main.accueil"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        nom_profil = request.form.get("nom_profil", "").strip()
        email = request.form.get("email", "").strip().lower()
        date_naissance = _parse_date(request.form.get("date_naissance"))
        profession = request.form.get("profession", "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "")
        confirmation = request.form.get("confirmation", "")

        erreurs = []
        if not nom or not nom_profil or not email or not mot_de_passe:
            erreurs.append("Nom, nom de profil, email et mot de passe sont obligatoires.")
        if not date_naissance:
            erreurs.append("Merci d'indiquer une date de naissance valide.")
        if mot_de_passe != confirmation:
            erreurs.append("Les mots de passe ne correspondent pas.")
        if len(mot_de_passe) < 6:
            erreurs.append("Le mot de passe doit contenir au moins 6 caractères.")
        if User.query.filter_by(email=email).first():
            erreurs.append("Un compte existe déjà avec cet email.")

        if erreurs:
            for e in erreurs:
                flash(e, "error")
            return render_template(
                "auth/inscription.html",
                nom=nom, email=email, nom_profil=nom_profil, profession=profession,
            )

        utilisateur = User(
            nom=nom,
            nom_profil=nom_profil,
            email=email,
            date_naissance=date_naissance,
            profession=profession,
        )
        utilisateur.set_password(mot_de_passe)
        db.session.add(utilisateur)
        db.session.flush()  # pour récupérer utilisateur.id

        profil_famille = FamilyMember(
            nom=nom_profil,
            date_naissance=date_naissance,
            profession=profession,
            est_soi=True,
            proprietaire_id=utilisateur.id,
        )
        db.session.add(profil_famille)

        db.session.commit()

        flash("Compte créé avec succès. Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/inscription.html")


@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.accueil"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")

        utilisateur = User.query.filter_by(email=email).first()

        if utilisateur and utilisateur.check_password(mot_de_passe):
            login_user(utilisateur, remember=True)
            page_suivante = request.args.get("next")
            flash(f"Bienvenue, {utilisateur.nom_profil or utilisateur.nom} !", "success")
            return redirect(page_suivante or url_for("main.accueil"))

        flash("Email ou mot de passe incorrect.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("main.accueil"))