"""
Migrations idempotentes : ajoutent les nouvelles colonnes aux tables déjà
existantes sur la base en ligne (Neon), et suppriment le contenu d'exemple
inséré au tout début du projet (profils, événements, patrimoine démo).

Chaque instruction tourne dans sa PROPRE transaction : si l'une d'elles
échoue, les autres s'appliquent quand même (contrairement à une transaction
partagée, où un seul échec annule tout le reste silencieusement).
"""
from sqlalchemy import text

from extensions import db


def appliquer_migrations():
    instructions = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS nom_profil VARCHAR(100)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS date_naissance DATE",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS profession VARCHAR(200)",
        "ALTER TABLE family_members ADD COLUMN IF NOT EXISTS profession VARCHAR(200)",
        "ALTER TABLE family_members ADD COLUMN IF NOT EXISTS lien_parente VARCHAR(50)",
        "ALTER TABLE family_members ADD COLUMN IF NOT EXISTS est_soi BOOLEAN DEFAULT FALSE",
        "ALTER TABLE family_members ADD COLUMN IF NOT EXISTS proprietaire_id INTEGER REFERENCES users(id)",
        "ALTER TABLE family_members ADD COLUMN IF NOT EXISTS photo_data TEXT",
    ]
    for instruction in instructions:
        try:
            with db.engine.begin() as connexion:
                connexion.execute(text(instruction))
        except Exception as erreur:
            # SQLite (tests locaux) ne supporte pas toujours IF NOT EXISTS sur ADD COLUMN ;
            # sur une base fraîche, les colonnes existent déjà via create_all().
            print(f"[migrations] instruction ignorée ({instruction!r}) : {erreur}")


def purger_profils_demo():
    from models import FamilyMember

    noms_demo = ["Jean AGBE", "Paul AGBE", "Aaron AGBE"]
    FamilyMember.query.filter(
        FamilyMember.nom.in_(noms_demo),
        FamilyMember.proprietaire_id.is_(None),
    ).delete(synchronize_session=False)
    db.session.commit()


def purger_contenu_demo():
    from models import Event, HeritageItem

    titres_evenements_demo = [
        "Réunion familiale annuelle",
        "Anniversaire de mariage des grands-parents",
    ]
    titres_patrimoine_demo = ["Maison familiale", "Terrain agricole"]

    Event.query.filter(Event.titre.in_(titres_evenements_demo)).delete(synchronize_session=False)
    HeritageItem.query.filter(HeritageItem.titre.in_(titres_patrimoine_demo)).delete(synchronize_session=False)
    db.session.commit()