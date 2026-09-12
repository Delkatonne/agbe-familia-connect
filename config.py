import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clé secrète pour les sessions Flask (cookies signés, protection CSRF de base)
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    # URL de connexion à la base PostgreSQL (Neon ou Aiven)
    # Format attendu : postgresql://user:password@host:port/dbname?sslmode=require
    _db_url = os.environ.get("DATABASE_URL", "")

    # SQLAlchemy attend "postgresql://", certains fournisseurs renvoient "postgres://"
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
