"""Anchovy"""
import os
import random
import uuid
from datetime import timedelta, datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy import text
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(override=False)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


class User(UserMixin, db.Model):
    """Store user information"""
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    invite = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    wallet_balance = db.Column(db.Float, default=0)
    invite_earnings = db.Column(db.Float, default=0)
    team_income = db.Column(db.Float, default=0)
    points = db.Column(db.Integer, default=0)


class RentedMiner(db.Model):
    """Store user mining data"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    miner_name = db.Column(db.String(50))
    computing = db.Column(db.String(50))
    price = db.Column(db.Float)
    net_income = db.Column(db.Float)
    total_revenue = db.Column(db.Float)
    current_income = db.Column(db.Float, default=0.0)
    purchase_time = db.Column(db.DateTime)
    expiry_time = db.Column(db.DateTime)
    validity_days = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(250))
    last_paid = db.Column(db.DateTime, nullable=True)


class Transaction(db.Model):
    """Store transanction information"""
    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usd_amount = db.Column(db.Float)
    naira_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Withdrawal(db.Model):
    """Store withdrawal requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)   # amount requested
    fee = db.Column(db.Float)   # 10% fee
    net_amount = db.Column(db.Float)   # amount after fee
    account_name = db.Column(db.String(150))
    account_number = db.Column(db.String(15))
    bank_name = db.Column(db.String(150))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship(
        'User', backref=db.backref('withdrawals', lazy=True))


class BankAccount(db.Model):
    """Store user's withdrawal bank account"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(10), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', backref=db.backref(
        'bank_account', uselist=False))

    def __repr__(self):
        return f"<User {self.phone}>"


def create_app():
    """Create and configure a Flask application"""
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=15)

    database_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Use psycopg v3 driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
    FLW_SECRET_HASH = os.getenv("FLW_SECRET_HASH")
    PAYMENT_EMAIL = os.getenv("PAYMENT_EMAIL")
    BASE_URL = os.getenv("BASE_URL")
    INVITE_REWARD = float(os.getenv("INVITE_REWARD", 0.2))
    EXCHANGE_RATE = float(os.getenv("EXCHANGE_RATE", 1500))

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "login"

    @app.route("/api/claim-signin", methods=["POST"])
    @login_required
    def claim_signin():
        data = request.get_json()
        pts = int(data.get("points", 1))
        current_user.points += pts
        db.session.commit()
        return jsonify({"success": True, "points": current_user.points})

    @app.route("/database/db")
    @login_required
    def database_db():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}, 200
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500

    @app.route("/home")
    @login_required
    def home():
        return render_template("home.html", user=current_user)

    @app.route("/mine")
    @login_required
    def mine():
        return render_template("mine.html", user=current_user)

    @app.route("/invite")
    @login_required
    def invite():
        total_invited = User.query.filter_by(
            invite=str(current_user.id)).count()
        invite_link = f"{BASE_URL}/register?ref={current_user.id}"

        return render_template(
            "invite.html",
            user=current_user,
            invite_link=invite_link,
            total_invited=total_invited,
            reward=INVITE_REWARD
        )

    @app.route("/shop-tier1")
    @login_required
    def shop_tier1():
        # Level 1 — users directly invited by current user with active miners
        level1_users = User.query.filter_by(invite=str(current_user.id)).all()
        level1_ids = [u.id for u in level1_users]
        level1_active = User.query.filter(
            User.invite == str(current_user.id)
        ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
            RentedMiner.active == True
        ).distinct().count()

        # Level 2 — users invited by level 1 users with active miners
        level2_active = 0
        if level1_ids:
            level2_active = User.query.filter(
                User.invite.in_([str(i) for i in level1_ids])
            ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
                RentedMiner.active == True
            ).distinct().count()

        # Level 3 — users invited by level 2 users with active miners
        level2_users = User.query.filter(
            User.invite.in_([str(i) for i in level1_ids])
        ).all() if level1_ids else []
        level2_ids = [u.id for u in level2_users]

        level3_active = 0
        if level2_ids:
            level3_active = User.query.filter(
                User.invite.in_([str(i) for i in level2_ids])
            ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
                RentedMiner.active == True
            ).distinct().count()

        return render_template(
            "shop-tier1.html",
            user=current_user,
            level1_active=level1_active,
            level2_active=level2_active,
            level3_active=level3_active
        )

        return render_template("shop-tier2.html", user=current_user)

    @app.route("/shop-tier2")
    @login_required
    def shop_tier2():
        level1_users = User.query.filter_by(invite=str(current_user.id)).all()
        level1_ids = [u.id for u in level1_users]

        level1_active = User.query.filter(
            User.invite == str(current_user.id)
        ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
            RentedMiner.active == True
        ).distinct().count()

        level2_users = User.query.filter(
            User.invite.in_([str(i) for i in level1_ids])
        ).all() if level1_ids else []
        level2_ids = [u.id for u in level2_users]

        level2_active = User.query.filter(
            User.invite.in_([str(i) for i in level1_ids])
        ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
            RentedMiner.active == True
        ).distinct().count() if level1_ids else 0

        level3_active = User.query.filter(
            User.invite.in_([str(i) for i in level2_ids])
        ).join(RentedMiner, RentedMiner.user_id == User.id).filter(
            RentedMiner.active == True
        ).distinct().count() if level2_ids else 0

        total_active = level1_active + level2_active + level3_active

        return render_template(
            "shop-tier2.html",
            user=current_user,
            level1_active=level1_active,
            level2_active=level2_active,
            level3_active=level3_active,
            total_active=total_active
        )

    @app.route("/pledge")
    @login_required
    def pledge():
        return render_template("pledge.html")

    @app.route("/apply-settings")
    @login_required
    def apply_settings():
        return render_template("apply-settings.html")

    @app.route("/miner-running")
    @login_required
    def miner_running():
        miners = RentedMiner.query.filter_by(
            user_id=current_user.id, active=True
        ).all()
        return render_template("miner-running.html", miners=miners, now=datetime.utcnow())

    @app.route("/rent-miner", methods=["POST"])
    @login_required
    def rent_miner():
        data = request.get_json()
        price = float(data.get("price"))
        validity = int(data.get("validity"))
        limit = int(data.get("limit"))
        name = data.get("name")

        already_rented = RentedMiner.query.filter_by(
            user_id=current_user.id,
            miner_name=name
        ).count()

        if already_rented >= limit:
            return jsonify({"success": False, "error": "purchase_limit"})

        if current_user.wallet_balance < price:
            return jsonify({"success": False, "error": "Insufficient balance"})

        current_user.wallet_balance -= price
        is_first_miner = RentedMiner.query.filter_by(
            user_id=current_user.id).count() == 0
        if is_first_miner and current_user.invite.isdigit():
            inviter = User.query.filter_by(id=int(current_user.invite)).first()
            if inviter:
                inviter.points += 500

        new_miner = RentedMiner(
            user_id=current_user.id,
            miner_name=name,
            computing=data.get("computing"),
            price=price,
            net_income=float(data.get("income")),
            total_revenue=float(data.get("totalRevenue")),
            validity_days=validity,
            purchase_time=datetime.utcnow(),
            expiry_time=datetime.utcnow() + timedelta(days=validity),
            image=data.get("image"),
            active=True
        )
        db.session.add(new_miner)
        db.session.commit()
        return jsonify({"success": True})

    @app.route("/api/my-miners")
    @login_required
    def api_my_miners():
        miners = RentedMiner.query.filter_by(user_id=current_user.id).all()
        return jsonify([{"name": m.miner_name} for m in miners])

    @app.route("/miner-completed")
    @login_required
    def miner_completed():
        miners = RentedMiner.query.filter_by(
            user_id=current_user.id, active=False
        ).all()
        return render_template("miner-completed.html", miners=miners, now=datetime.utcnow())

    @app.route("/bonus")
    @login_required
    def bonus():
        return render_template("bonus.html", user=current_user)

    @app.route("/company")
    @login_required
    def company():
        return render_template("company.html")

    @app.route("/exchange", methods=["GET", "POST"])
    @login_required
    def exchange():
        errors = []
        success = None

        if request.method == "POST":
            try:
                points_to_exchange = int(request.form.get("points", 0))
            except ValueError:
                points_to_exchange = 0

            if points_to_exchange < 500:
                errors.append("Minimum exchange is 500 points.")
            elif points_to_exchange > current_user.points:
                errors.append("You don't have enough points.")
            else:
                # Floor divide — 501 points = $1, not $1.002
                usd_earned = points_to_exchange // 500
                leftover = points_to_exchange % 500  # unspent points kept

                current_user.points -= (points_to_exchange - leftover)
                current_user.wallet_balance += usd_earned

                db.session.commit()
                success = f"Successfully exchanged {points_to_exchange - leftover} points for ${usd_earned}.00!"

        return render_template("exchange.html", user=current_user, errors=errors, success=success)

    @app.route("/raffle")
    @login_required
    def raffle():
        return render_template("raffle.html")

    @app.route("/team")
    @login_required
    def team():
        # ── Level 1 ──
        level1_users = User.query.filter_by(invite=str(current_user.id)).all()
        level1_ids = [u.id for u in level1_users]

        level1_data = []
        for u in level1_users:
            has_miner = RentedMiner.query.filter_by(
                user_id=u.id, active=True).first() is not None
            level1_data.append(
                {"id": u.id, "phone": u.phone, "active": has_miner})

        # ── Level 2 ──
        level2_users = User.query.filter(
            User.invite.in_([str(i) for i in level1_ids])
        ).all() if level1_ids else []
        level2_ids = [u.id for u in level2_users]

        level2_data = []
        for u in level2_users:
            has_miner = RentedMiner.query.filter_by(
                user_id=u.id, active=True).first() is not None
            level2_data.append(
                {"id": u.id, "phone": u.phone, "active": has_miner})

        # ── Level 3 ──
        level3_users = User.query.filter(
            User.invite.in_([str(i) for i in level2_ids])
        ).all() if level2_ids else []

        level3_data = []
        for u in level3_users:
            has_miner = RentedMiner.query.filter_by(
                user_id=u.id, active=True).first() is not None
            level3_data.append(
                {"id": u.id, "phone": u.phone, "active": has_miner})

        return render_template(
            "team.html",
            level1=level1_data,
            level2=level2_data,
            level3=level3_data
        )

    @app.route("/cs-exchange")
    @login_required
    def cs_exchange():
        return render_template("cs-exchange.html")

    @app.route("/withdrawhistory")
    @login_required
    def withdrawhistory():
        return render_template("withdrawhistory.html", user=current_user)

    @app.route("/recharge")
    @login_required
    def recharge():
        return render_template("recharge.html", user=current_user)

    @app.route("/withdraw", methods=["GET", "POST"])
    @login_required
    def withdraw():
        account = BankAccount.query.filter_by(user_id=current_user.id).first()
        errors = []
        success = None

        if request.method == "POST":
            # ── Must have a saved bank account ──
            if not account:
                errors.append(
                    "You must save a bank account before withdrawing.")

            else:
                try:
                    amount = float(request.form.get("amount", 0))
                except ValueError:
                    amount = 0

                fee = round(amount * 0.10, 2)
                net_amount = round(amount - fee, 2)

                # ── Validations ──
                if amount > 1000:
                    errors.append("Maximum withdraw amount is $1000")
                elif amount < 5:
                    errors.append("Minimum withdrawal amount is $5.")
                elif amount > current_user.wallet_balance:
                    errors.append("Insufficient balance.")
                else:
                    # ── Deduct immediately, mark pending ──
                    current_user.wallet_balance -= amount

                    withdrawal = Withdrawal(
                        user_id=current_user.id,
                        amount=amount,
                        fee=fee,
                        net_amount=net_amount,
                        account_name=account.account_name,
                        account_number=account.account_number,
                        bank_name=account.bank_name,
                        status="pending"
                    )
                    db.session.add(withdrawal)
                    db.session.commit()
                    success = f"Withdrawal request of ${amount} submitted. You will receive ${net_amount} after the 10% fee."

        return render_template(
            "withdraw.html",
            user=current_user,
            account=account,
            errors=errors,
            success=success
        )

    @app.route("/admin/withdrawals")
    @login_required
    def admin_withdrawals():
        # Simple admin check — only user with id 1 or ADMIN invite
        if current_user.invite != "ADMIN":
            return "Unauthorized", 403
        withdrawals = Withdrawal.query.order_by(
            Withdrawal.created_at.desc()
        ).all()
        return render_template("admin-withdrawals.html", withdrawals=withdrawals)

    @app.route("/admin/withdrawals/<int:wid>/approve", methods=["POST"])
    @login_required
    def approve_withdrawal(wid):
        if current_user.invite != "ADMIN":
            return "Unauthorized", 403
        w = Withdrawal.query.get_or_404(wid)
        w.status = "approved"
        db.session.commit()
        return redirect(url_for("admin_withdrawals"))

    @app.route("/admin/withdrawals/<int:wid>/reject", methods=["POST"])
    @login_required
    def reject_withdrawal(wid):
        if current_user.invite != "ADMIN":
            return "Unauthorized", 403
        w = Withdrawal.query.get_or_404(wid)
        if w.status == "pending":
            # Refund the user
            user = db.session.get(User, w.user_id)
            user.wallet_balance += w.amount
        w.status = "rejected"
        db.session.commit()
        return redirect(url_for("admin_withdrawals"))

    @app.route("/bank", methods=["GET", "POST"])
    @login_required
    def bank():
        account = BankAccount.query.filter_by(user_id=current_user.id).first()
        errors = []

        if request.method == "POST":
            account_name = (request.form.get("account_name") or "").strip()
            account_number = (request.form.get("account_number") or "").strip()
            bank_name = (request.form.get("bank_name") or "").strip()

            if not account_name:
                errors.append("Account name is required")
            if not account_number.isdigit() or len(account_number) != 10:
                errors.append("Account number must be exactly 10 digits")
            if not bank_name:
                errors.append("Bank name is required")

            if not errors:
                if account:
                    # ✅ Update existing
                    account.account_name = account_name
                    account.account_number = account_number
                    account.bank_name = bank_name
                else:
                    # ✅ Create new
                    account = BankAccount(
                        user_id=current_user.id,
                        account_name=account_name,
                        account_number=account_number,
                        bank_name=bank_name
                    )
                    db.session.add(account)

                db.session.commit()
                return redirect(url_for("bank"))

        return render_template("bank.html", account=account, errors=errors)

    @app.route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password():
        errors = []
        if request.method == "POST":
            current_pw = request.form.get("current_password") or ""
            new_pw = request.form.get("new_password") or ""
            confirm_pw = request.form.get("confirm_password") or ""

            if not check_password_hash(current_user.password_hash, current_pw):
                errors.append("Current password is incorrect")

            if len(new_pw) < 6:
                errors.append("New password needs to at least 6 characters")

            if new_pw != confirm_pw:
                errors.append("New password and confirmation do not match")

            if not errors:
                current_user.password_hash = generate_password_hash(new_pw)
                db.session.commit()
                return redirect(url_for("login"))

        return render_template("change-password.html", errors=errors)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        errors = []
        prefilled_invite = request.args.get("ref", "")
        is_first_user = User.query.count() == 0

        if request.method == "POST":
            phone = (request.form.get("phone") or "").strip()
            invite = (request.form.get("invite") or "").strip()
            password = request.form.get("password")
            confirm = request.form.get("confirm_password")

            if not (len(phone) == 11):
                errors.append(
                    "Phone number is invalid")

            if len(password) < 6:
                errors.append("Password needs to be at least 6 characters")

            if password != confirm:
                errors.append("Passwords don't match")

            inviter = None
            if not is_first_user:
                if not invite:
                    errors.append("An invitation code is required to register")
                else:
                    inviter = User.query.filter_by(
                        id=int(invite)).first() if invite.isdigit() else None
                    if not inviter:
                        errors.append("Invalid invitation code")

            if not errors:
                try:
                    while True:
                        random_id = random.randint(100000, 999999)
                        if not User.query.filter_by(id=random_id).first():
                            break

                    pw_hash = generate_password_hash(password)
                    user = User(
                        id=random_id,
                        phone=phone,
                        invite=invite if invite else "ADMIN",
                        password_hash=pw_hash
                    )
                    db.session.add(user)
                    if inviter:
                        inviter.wallet_balance += INVITE_REWARD
                        inviter.invite_earnings += INVITE_REWARD

                    db.session.commit()
                    return redirect(url_for('login'))

                except IntegrityError:
                    db.session.rollback()
                    errors.append("that phone number is already registered")

        return render_template("register.html", errors=errors, prefilled_invite=prefilled_invite, is_first_user=is_first_user)

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
                    remember_flag = request.form.get('remember') == "1"
                    login_user(user, remember=remember_flag)
                    return redirect(url_for('home'))

        return render_template("login.html", errors=errors)

    @login_manager.user_loader
    def load_user(user_id):
        # TODO: query your database for the user
        return db.session.get(User, int(user_id))

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/api/balance")
    @login_required
    def api_balance():
        return jsonify({
            "balance": round(current_user.wallet_balance, 2)
        })

    @app.route("/api/income")
    @login_required
    def api_income():
        return jsonify({
            "balance": round(current_user.team_income, 2)
        })

    @app.route("/api/points")
    @login_required
    def api_points():
        return jsonify({"points": current_user.points})

    @app.route('/payment', methods=['POST'])
    @login_required
    def payment():
        try:
            usd_amount = float(request.form["usd_amount"])
        except (ValueError, KeyError):
            return "Invalid amount", 400

        if usd_amount < 1:
            return "Minimum deposit is $1", 400

        usd_amount = float(request.form["usd_amount"])
        naira_amount = usd_amount * EXCHANGE_RATE

        tx_ref = str(uuid.uuid4())

        transaction = Transaction(
            tx_ref=tx_ref,
            user_id=current_user.id,
            naira_amount=naira_amount,
            usd_amount=usd_amount,
            status="pending"
        )
        db.session.add(transaction)
        db.session.commit()

        url = "https://api.flutterwave.com/v3/charges?type=bank_transfer"
        headers = {
            "Authorization": f"Bearer {FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "tx_ref": tx_ref,
            "amount": naira_amount,
            "currency": "NGN",
            "email": PAYMENT_EMAIL,
            "redirect_url": f"{BASE_URL}/success",
            "payment_type": "banktransfer",
            "customer": {
                "phonenumber": current_user.phone,
                "name": "User"
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("status") == "success" and data.get("meta"):
            payment_data = data["meta"]["authorization"]
            session['pending_tx_ref'] = tx_ref

            return render_template(
                "payment.html",
                account_number=payment_data["transfer_account"],
                bank_name=payment_data["transfer_bank"],
                account_name="Issa Abdullahi",
                note=f"CSM{current_user.id}",
                amount=payment_data["transfer_amount"],
                expires_in=30 * 60
            )
        else:
            return str(data)

    @app.route("/check-payment")
    @login_required
    def check_payment():
        tx_ref = session.get('pending_tx_ref')  # get it from session

        if not tx_ref:
            return jsonify({"status": "not_found"}), 404

        transaction = Transaction.query.filter_by(
            tx_ref=tx_ref,
            user_id=current_user.id
        ).first()

        if not transaction:
            return jsonify({"status": "not_found"}), 404

        if transaction.status == "successful":
            session.pop('pending_tx_ref', None)

        return jsonify({"status": transaction.status})

    @app.route('/webhook', methods=['POST'])
    def webhook():
        secret_hash = request.headers.get("verif-hash")

        if secret_hash != FLW_SECRET_HASH:
            app.logger.warning(f"Invalid webhook hash attempt")
            return "Unauthorized", 403

        data = request.json

        if not data:
            return "Bad Request", 400

        if data.get("event") == "charge.completed":

            tx_ref = data["data"]["tx_ref"]
            status = data["data"]["status"]
            amount = data["data"]["amount"]

            transaction = Transaction.query.filter_by(tx_ref=tx_ref).first()
            if not transaction:
                return "Transaction not found", 404
            if transaction.status == "successful":
                return "Already processed", 200

            if (transaction and transaction.status != "successful"
                    and status == "successful" and abs(amount - transaction.naira_amount) < 1):
                transaction.status = "successful"

                user = db.session.get(User, transaction.user_id)
                if not user:
                    return "User not found", 400
                user.wallet_balance += transaction.usd_amount

                db.session.commit()

        return "OK", 200

    @app.route("/success")
    @login_required
    def success():
        return render_template("success.html")

    @app.route("/transactions")
    @login_required
    def transactions_page():

        transactions = Transaction.query.filter_by(
            user_id=current_user.id,
            status="successful"
        ).order_by(Transaction.id.desc()).all()

        return render_template("transactions.html", transactions=transactions)

    with app.app_context():
        db.create_all()

    def pay_miner_income():
        """Runs every 24h — credits daily income and referral bonuses."""
        with app.app_context():
            now = datetime.utcnow()

            # Get all active miners due for payment
            active_miners = RentedMiner.query.filter_by(active=True).all()

            for miner in active_miners:

                # Skip if expired
                if now >= miner.expiry_time:
                    miner.active = False
                    db.session.commit()
                    continue

                # Skip if paid in last 24 hours
                if miner.last_paid and (now - miner.last_paid).total_seconds() < 86400:
                    continue

                daily = miner.net_income
                renter = db.session.get(User, miner.user_id)
                if not renter:
                    continue

                # ── Pay the renter ──────────────────────────
                renter.wallet_balance += daily
                miner.current_income += daily
                miner.last_paid = now

                # ── Level 1 referral (who invited the renter) ──
                level1 = User.query.filter_by(
                    id=int(renter.invite)
                ).first() if renter.invite.isdigit() else None

                if level1:
                    level1_cut = round(daily * 0.10, 4)
                    level1.team_income += level1_cut
                    level1.invite_earnings += level1_cut

                    # ── Level 2 referral (who invited level1) ──
                    level2 = User.query.filter_by(
                        id=int(level1.invite)
                    ).first() if level1.invite.isdigit() else None

                    if level2:
                        level2_cut = round(daily * 0.05, 4)
                        level2.team_income += level2_cut
                        level2.invite_earnings += level2_cut

                        # ── Level 3 referral (who invited level2) ──
                        level3 = User.query.filter_by(
                            id=int(level2.invite)
                        ).first() if level2.invite.isdigit() else None

                        if level3:
                            level3_cut = round(daily * 0.025, 4)
                            level3.team_income += level3_cut
                            level3.invite_earnings += level3_cut

            db.session.commit()

    # ── Start scheduler ─────────────────────────────────────
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=pay_miner_income,
        trigger='interval',
        hours=24,
        id='miner_payout',
        replace_existing=True
    )
    scheduler.start()

    # Shut down scheduler cleanly when app exits
    import atexit
    atexit.register(lambda: scheduler.shutdown(wait=False))

    return app


DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')


def add_column_if_missing(cursor, table, column, col_type):
    cursor.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in cursor.fetchall()]
    if column not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"✓ Added: {table}.{column}")
    else:
        print(f"— Skipped (exists): {table}.{column}")


def run():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Running migrations...\n")

    # ── Add your columns here ──
    add_column_if_missing(cursor, 'user', 'points',
                          'INTEGER DEFAULT 0')
    add_column_if_missing(cursor, 'user', 'team_income',     'FLOAT DEFAULT 0')
    add_column_if_missing(cursor, 'user', 'invite_earnings', 'FLOAT DEFAULT 0')
    add_column_if_missing(cursor, 'rented_miner', 'last_paid', 'DATETIME')
    add_column_if_missing(cursor, 'rented_miner', 'image',     'VARCHAR(250)')
    add_column_if_missing(cursor, 'withdrawal',
                          'fee',        'FLOAT DEFAULT 0')
    add_column_if_missing(cursor, 'withdrawal',
                          'net_amount', 'FLOAT DEFAULT 0')

    conn.commit()
    conn.close()
    print("\n✅ Migration complete.")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, port=5000)
