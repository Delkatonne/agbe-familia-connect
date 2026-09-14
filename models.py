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
    telephone = db.Column(db.String(30), nullable=True)
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
    telephone = db.Column(db.String(30), nullable=True)
    photo_url = db.Column(db.String(300), nullable=True)
    photo_data = db.Column(db.Text, nullable=True)  # photo de profil actuelle (data URI base64)
    profession = db.Column(db.String(200), nullable=True)

    # Lien de parenté affiché (ex: "Père", "Mère", "Autre") — vide si c'est le profil de l'utilisateur lui-même
    lien_parente = db.Column(db.String(50), nullable=True)
    # True si cette fiche représente l'utilisateur connecté lui-même (créée à l'inscription)
    est_soi = db.Column(db.Boolean, default=False)
    # L'utilisateur qui gère cette fiche (lui-même, ou l'un de ses parents qu'il a ajouté)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    proprietaire = db.relationship("User", foreign_keys=[proprietaire_id], backref="membres_ajoutes")

    # Liens père/mère (pour l'arbre généalogique) — renseignés automatiquement
    # quand l'utilisateur ajoute un parent avec le lien "Père" ou "Mère"
    pere_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=True)
    mere_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=True)
    pere = db.relationship("FamilyMember", foreign_keys=[pere_id], remote_side=[id])
    mere = db.relationship("FamilyMember", foreign_keys=[mere_id], remote_side=[id])

    def __repr__(self):
        return f"<FamilyMember {self.nom}>"


class ChampPersonnalise(db.Model):
    """Information libre qu'un membre ajoute à son profil (ou à celui d'un parent qu'il gère)."""
    __tablename__ = "champs_personnalises"

    id = db.Column(db.Integer, primary_key=True)
    family_member_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    valeur = db.Column(db.Text, nullable=False)

    membre = db.relationship(
        "FamilyMember",
        backref=db.backref("champs_personnalises", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<ChampPersonnalise {self.titre}>"


class PhotoGalerie(db.Model):
    """Photo, vidéo ou audio partagé dans la galerie familiale."""
    __tablename__ = "photos_galerie"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    photo_data = db.Column(db.Text, nullable=False)
    type_media = db.Column(db.String(10), nullable=False, default="image")  # image, video ou audio
    proprietaire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    proprietaire = db.relationship("User", backref="photos_ajoutees")

    def __repr__(self):
        return f"<PhotoGalerie {self.titre}>"


class PhotoProfil(db.Model):
    """Historique des anciennes photos de profil d'un membre (comme sur Facebook)."""
    __tablename__ = "photos_profil_historique"

    id = db.Column(db.Integer, primary_key=True)
    family_member_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=False)
    photo_data = db.Column(db.Text, nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    membre = db.relationship(
        "FamilyMember",
        backref=db.backref(
            "anciennes_photos",
            cascade="all, delete-orphan",
            order_by="PhotoProfil.date_ajout.desc()",
        ),
    )

    def __repr__(self):
        return f"<PhotoProfil membre={self.family_member_id}>"


class Publication(db.Model):
    """Publication sur le journal d'actualité d'un membre (comme un mur Facebook)."""
    __tablename__ = "publications"

    id = db.Column(db.Integer, primary_key=True)
    family_member_id = db.Column(db.Integer, db.ForeignKey("family_members.id"), nullable=False)
    auteur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    photo_data = db.Column(db.Text, nullable=True)
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)

    membre = db.relationship(
        "FamilyMember",
        backref=db.backref(
            "publications",
            cascade="all, delete-orphan",
            order_by="Publication.date_publication.desc()",
        ),
    )
    auteur = db.relationship("User")

    def __repr__(self):
        return f"<Publication {self.id}>"


class Message(db.Model):
    """Message privé entre deux membres inscrits."""
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    expediteur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    destinataire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    lu = db.Column(db.Boolean, default=False)

    expediteur = db.relationship("User", foreign_keys=[expediteur_id])
    destinataire = db.relationship("User", foreign_keys=[destinataire_id])

    def __repr__(self):
        return f"<Message {self.expediteur_id} -> {self.destinataire_id}>"


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_evenement = db.Column(db.Date, nullable=False)
    lieu = db.Column(db.String(200), nullable=True)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    proprietaire = db.relationship("User", backref="evenements_ajoutes")

    def __repr__(self):
        return f"<Event {self.titre}>"


class HeritageItem(db.Model):
    """Élément du patrimoine familial (maison, objet, terrain, document...)."""
    __tablename__ = "heritage_items"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(300), nullable=True)
    photo_data = db.Column(db.Text, nullable=True)
    proprietaire_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    proprietaire = db.relationship("User", backref="patrimoine_ajoute")

    def __repr__(self):
        return f"<HeritageItem {self.titre}>"