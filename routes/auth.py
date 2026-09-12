from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("main.accueil"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")
        confirmation = request.form.get("confirmation", "")

        erreurs = []
        if not nom or not email or not mot_de_passe:
            erreurs.append("Tous les champs sont obligatoires.")
        if mot_de_passe != confirmation:
            erreurs.append("Les mots de passe ne correspondent pas.")
        if len(mot_de_passe) < 6:
            erreurs.append("Le mot de passe doit contenir au moins 6 caractères.")
        if User.query.filter_by(email=email).first():
            erreurs.append("Un compte existe déjà avec cet email.")

        if erreurs:
            for e in erreurs:
                flash(e, "error")
            return render_template("auth/inscription.html", nom=nom, email=email)

        utilisateur = User(nom=nom, email=email)
        utilisateur.set_password(mot_de_passe)
        db.session.add(utilisateur)
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
            login_user(utilisateur)
            page_suivante = request.args.get("next")
            flash(f"Bienvenue, {utilisateur.nom} !", "success")
            return redirect(page_suivante or url_for("main.accueil"))

        flash("Email ou mot de passe incorrect.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("main.accueil"))
