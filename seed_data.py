"""
Contenu d'exemple pour les événements et le patrimoine, inséré une seule
fois (chaque bloc vérifie que la table est vide avant d'ajouter).

Les profils de membres ne sont PAS créés ici : chaque personne crée le
sien en s'inscrivant sur le site, dans "Mon espace".
"""
from datetime import date

from extensions import db
from models import Event, HeritageItem


def inserer_contenu_exemple():
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