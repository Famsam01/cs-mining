"""This module creates and runs a simple Flask web application."""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    invite = db.Column(db.String(5), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.phone}>"


def create_app():
    """Create and configure a Flask application.

    Returns:
        Flask: The configured Flask app instance.
    """
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'famsamoj-secret-key-1234.'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @app.route("/database/db")
    def database_db():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}, 200
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500

    with app.app_context():
        db.create_all()

    @app.route("/home")
    @login_required
    def home():
        return render_template("home.html")

    @app.route("/mine")
    @login_required
    def mine():
        return render_template("mine.html")

    @app.route("/invite")
    @login_required
    def invite():
        return render_template("invite.html")

    @app.route("/shop")
    @login_required
    def shop():
        return render_template("shop-tier1.html")

    @app.route("/pledge")
    @login_required
    def pledge():
        return render_template("pledge.html")

    @app.route("/register", methods=["GET", "POST"])
    @login_required
    def register():
        errors = []

        if request.method == "POST":
            phone = (request.form.get("phone") or "").strip()
            invite = (request.form.get("invite") or "").strip()
            password = request.form.get("password")
            confirm = request.form.get("confirm_password")

            if not (10 <= len(phone) <= 15):
                errors.append(
                    "Phone number must be between 10 to 15 characters")

            if len(password) < 6:
                errors.append("Password needs to be at least 6 characters")

            if password != confirm:
                errors.append("Passwords don't match")

            if not errors:
                try:
                    pw_hash = generate_password_hash(password)
                    user = User(phone=phone, invite=invite,
                                password_hash=pw_hash)
                    db.session.add(user)
                    db.session.commit()

                    return redirect(url_for('login'))

                except IntegrityError:
                    db.session.rollback()
                    errors.append("that phone number is already registered")

        return render_template("register.html", errors=errors)

    @app.route("/", methods=["GET", "POST"])
    def login():
        errors = []

        if request.method == "POST":
            phone = (request.form.get("phone") or "").strip()
            password = request.form.get("password") or ""

            if not phone:
                errors.append("Phone number is required")

            if not password:
                errors.append("Password is required")

            if not errors:
                user = User.query.filter_by(phone=phone).first()

            if not user or not check_password_hash(user.password_hash, password):
                errors.append("Invalid Phone number or password")

            else:
                login_user(user)
                return redirect(url_for('home'))

        return render_template("login.html", errors=errors)

    @login_manager.user_loader
    def load_user(user_id):
        # TODO: query your database for the user
        return User.query.get(int(user_id))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
