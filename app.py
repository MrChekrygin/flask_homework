from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # регистрация blueprint'ов
    from routes.ads import ads_bp
    from routes.auth import auth_bp

    app.register_blueprint(ads_bp, url_prefix="/ads")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
