from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)

    # Wallet balance (in NGN kobo - integer)
    balance = db.Column(db.BigInteger, default=0)

    # Flutterwave Virtual Account Details
    flw_order_ref = db.Column(db.String(100), unique=True, nullable=True)
    flw_account_number = db.Column(db.String(20), unique=True, nullable=True)
    flw_bank_name = db.Column(db.String(50), nullable=True)
    flw_tx_ref = db.Column(db.String(100), unique=True, nullable=True)
    flw_is_permanent = db.Column(db.Boolean, default=False)
    flw_created_at = db.Column(db.DateTime, nullable=True)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.phone}>"

    def get_balance_ngn(self):
        return self.balance / 100

    def credit(self, amount_kobo):
        self.balance += amount_kobo
        return self.balance

    def debit(self, amount_kobo):
        if self.balance >= amount_kobo:
            self.balance -= amount_kobo
            return True
        return False


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal
    amount = db.Column(db.BigInteger, nullable=False)  # kobo
    currency = db.Column(db.String(3), default='NGN')

    status = db.Column(db.String(20), default='pending')
    reference = db.Column(db.String(100), unique=True,
                          nullable=False)  # Our ref
    external_ref = db.Column(
        db.String(100), nullable=True)  # Flutterwave tx_id
    flw_tx_ref = db.Column(db.String(100), nullable=True)  # Flutterwave tx_ref

    description = db.Column(db.String(255), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.reference} - {self.type} - {self.status}>"
