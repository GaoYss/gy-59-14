from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db
from .routes import register_blueprints
from .seed import seed_data


def _migrate_db(app):
    with app.app_context():
        inspector = db.inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns("rules")]
        if "quota_warning_threshold" not in columns:
            db.session.execute(
                db.text(
                    "ALTER TABLE rules ADD COLUMN quota_warning_threshold INTEGER"
                )
            )
            db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _migrate_db(app)
        seed_data()

    register_blueprints(app)

    @app.get("/api/health")
    def health_check():
        return {"status": "ok", "service": "driving-exam-booking"}

    return app
