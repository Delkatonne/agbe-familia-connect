"""
Contenu d'exemple inséré automatiquement au démarrage de l'application
(une seule fois : chaque bloc vérifie que la table est vide avant d'ajouter).
"""
from datetime import date

from extensions import db
from models import FamilyMember, Event, HeritageItem


def inserer_contenu_exemple():
    if FamilyMember.query.count() == 0:
        grand_pere = FamilyMember(
            nom="Jean AGBE",
            date_naissance=date(1945, 3, 12),
            date_deces=date(2018, 7, 4),
            biographie="Fondateur de la famille moderne, agriculteur et sage du village.",
            photo_url="/static/img/exemple-membre.jpg",
        )
        db.session.add(grand_pere)
        db.session.flush()

        pere = FamilyMember(
            nom="Paul AGBE",
            date_naissance=date(1970, 6, 20),
            biographie="Fils aîné, enseignant et responsable du patrimoine familial.",
            photo_url="/static/img/exemple-membre.jpg",
            parent_id=grand_pere.id,
        )
        db.session.add(pere)
        db.session.flush()

        enfant = FamilyMember(
            nom="Aaron AGBE",
            date_naissance=date(2000, 1, 15),
            biographie="Étudiant, passionné d'informatique et de technologie.",
            photo_url="/static/img/exemple-membre.jpg",
            parent_id=pere.id,
        )
        db.session.add(enfant)

    if Event.query.count() == 0:
        db.session.add_all([
            Event(
                titre="Réunion familiale annuelle",
                description="Grand rassemblement de toute la famille AGBE, exemple à modifier.",
                date_evenement=date(2026, 12, 25),
                lieu="Cotonou, Bénin",
            ),
            Event(
                titre="Anniversaire de mariage des grands-parents",
                description="Célébration commémorative, exemple à modifier.",
                date_evenement=date(2026, 9, 30),
                lieu="Porto-Novo, Bénin",
            ),
        ])

    if HeritageItem.query.count() == 0:
        db.session.add_all([
            HeritageItem(
                titre="Maison familiale",
                description="La maison ancestrale, construite en 1950, exemple à modifier.",
                photo_url="/static/img/exemple-patrimoine.jpg",
            ),
            HeritageItem(
                titre="Terrain agricole",
                description="Terrain transmis de génération en génération, exemple à modifier.",
                photo_url="/static/img/exemple-patrimoine.jpg",
            ),
        ])

    db.session.commit()