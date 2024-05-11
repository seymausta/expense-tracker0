from datetime import datetime, timezone
from typing import Optional
from time import time
import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship

from app import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=False)
    lastname: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                 unique=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    expenses: so.WriteOnlyMapped['Expense'] = so.relationship(
        back_populates='user',passive_deletes=True)
    incomes = so.relationship("Income", back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)

class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    expenses = db.relationship('Expense', backref='category', lazy=True)

    def __repr__(self):
        return '<Category {}>'.format(self.name)

class Expense(db.Model):
    __tablename__ = 'expenses'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    amount : so.Mapped[float] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    category_id : so.Mapped[int] = so.mapped_column(sa.ForeignKey(Category.id),index=True)
    date : so.Mapped[datetime] = so.mapped_column(sa.Date, nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    user: so.Mapped[User] = so.relationship(back_populates='expenses')

    def __repr__(self):
        return '<Expense {}>'.format(self.name)

class Income(db.Model):
    __tablename__ = 'income'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    amount: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    date: so.Mapped[datetime] = so.mapped_column(sa.Date, nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(db.ForeignKey('users.id'), nullable=False)

    user: so.Mapped[User]= so.relationship(back_populates='incomes')

    def __repr__(self):
        return f"Income(id={self.id}, name={self.name}, amount={self.amount}, user_id={self.user_id})"

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

