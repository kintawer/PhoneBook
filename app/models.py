from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from flask_login import UserMixin


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(15), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.relationship('Relation', backref='subject',
                               lazy='dynamic',
                               foreign_keys='Relation.subject_id')
    about_contacts = db.relationship('Relation', backref='owner',
                                     lazy='dynamic',
                                     foreign_keys='Relation.owner_id')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return '<User {} have id {} and phone number {}.>'.format(
            self.username, self.id, self.phone_number)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # def is_noted(self, user):
    #     for notes in self.about_contacts.all():
    #         return notes.subject_id == user.id

    def get_relation(self, user):
        for notes in self.about_contacts.all():
            if notes.subject_id == user.id:
                return notes

    def get_messages(self, user):
        return Message.query.join(Relation, (
                (Relation.owner_id == user.id) &
                (Relation.subject_id == self.id) &
                (Relation.id == Message.relation_id)
                ) | (
                (Relation.subject_id == user.id) &
                (Relation.owner_id == self.id) &
                (Relation.id == Message.relation_id)))\
            .order_by(Message.date.desc())


class Relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    username = db.Column(db.String(64), index=True, unique=True)
    note = db.Column(db.String(128))
    messages = db.relationship('Message', backref='relation', lazy='dynamic')

    def __repr__(self):
        return '<Entry {}. User {} ---> {}.>'.format(
            self.id, self.owner.username, self.subject.username)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    message = db.Column(db.String(256))
    relation_id = db.Column(db.Integer, db.ForeignKey('relation.id'))

    def __repr__(self):
        return '{} wrote a message to {} on {}'.format(
            self.relation.owner.username, self.relation.subject.username, self.date)

