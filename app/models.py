from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
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
        back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))

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

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))