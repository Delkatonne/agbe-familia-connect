from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    nom_profil = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    date_naissance = db.Column(db.Date, nullable=True)
    profession = db.Column(db.String(200), nullable=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, mot_de_passe):
        self.mot_de_passe_hash = generate_password_hash(mot_de_passe)

    def check_password(self, mot_de_passe):
        return check_password_hash(self.mot_de_passe_hash, mot_de_passe)

    def __repr__(self):
        return f"<User {self.email}>"


class FamilyMember(db.Model):
    __tablename__ = "family_members"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    date_naissance = db.Column(db.Date, nullable=True)
    date_deces = db.Column(db.Date, nullable=True)
    biographie = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(300), nullable=True)
    photo_data = db.Column(db.Text, nullable=True)  # image envoyée par l'utilisateur (data URI base64)
    profession = db.Column(db.String(200), nullable=True)

    # Lien de parenté affiché (ex: "Père", "Mère", "Autre") — vide si c'est le profil de l'utilisateur lui-même
    lien_parente = db.Column(db.String(50), nullable=True)
    # True si cette fiche représente l'utilisateur connecté lui-même (créée à l'inscription)
    est_soi = db.Column(db.Boolean, default=False)
    # L'utilisateur qui gère cette fiche (lui-même, ou l'un de ses parents qu'il a ajouté)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    proprietaire = db.relationship("User", foreign_keys=[proprietaire_id], backref="membres_ajoutes")

    # Lien vers un parent (pour construire un arbre généalogique simple)
    parent_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=True)
    enfants = db.relationship("FamilyMember", backref=db.backref("parent", remote_side=[id]), foreign_keys=[parent_id])

    def __repr__(self):
        return f"<FamilyMember {self.nom}>"


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_evenement = db.Column(db.Date, nullable=False)
    lieu = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Event {self.titre}>"


class HeritageItem(db.Model):
    """Élément du patrimoine familial (maison, objet, terrain, document...)."""
    __tablename__ = "heritage_items"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<HeritageItem {self.titre}>"