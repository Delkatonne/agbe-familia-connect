from flask import Flask

from config import Config
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.espace import espace_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(espace_bp)

    with app.app_context():
        from migrations import appliquer_migrations, purger_profils_demo, purger_contenu_demo

        db.create_all()
        appliquer_migrations()
        purger_profils_demo()
        purger_contenu_demo()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)