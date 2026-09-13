"""
Migrations idempotentes : ajoutent les nouvelles colonnes aux tables déjà
existantes sur la base en ligne (Neon), et suppriment une fois pour toutes
les profils d'exemple insérés au tout début du projet.

Tout est sans danger à exécuter plusieurs fois (à chaque démarrage) :
- les ALTER TABLE utilisent IF NOT EXISTS
- la purge ne cible que les 3 noms démo précis, sans propriétaire
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
    ]
    with db.engine.begin() as connexion:
        for instruction in instructions:
            try:
                connexion.execute(text(instruction))
            except Exception:
                # SQLite (tests locaux) ne supporte pas IF NOT EXISTS sur ADD COLUMN ;
                # sur une base fraîche, les colonnes existent déjà via create_all().
                pass


def purger_profils_demo():
    from models import FamilyMember

    noms_demo = ["Jean AGBE", "Paul AGBE", "Aaron AGBE"]
    FamilyMember.query.filter(
        FamilyMember.nom.in_(noms_demo),
        FamilyMember.proprietaire_id.is_(None),
    ).delete(synchronize_session=False)
    db.session.commit()