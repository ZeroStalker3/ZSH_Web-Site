from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    social_links = db.relationship('SocialLinks', backref='user', uselist=False)
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}')>"

    def friends(self):
        accepted = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == self.id, Friendship.status == 'accepted'),
                and_(Friendship.receiver_id == self.id, Friendship.status == 'accepted')
            )
        ).all()
        user_ids = [f.requester_id if f.requester_id != self.id else f.receiver_id for f in accepted]
        return User.query.filter(User.id.in_(user_ids)).all()

    def is_friend(self, other_user):
        return Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == self.id, Friendship.receiver_id == other_user.id),
                and_(Friendship.receiver_id == self.id, Friendship.requester_id == other_user.id)
            ),
            Friendship.status == 'accepted'
        ).count() > 0
    
    def get_friends_for_user(user_id):
        accepted = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == user_id, Friendship.status == 'accepted'),
                and_(Friendship.receiver_id == user_id, Friendship.status == 'accepted')
            )
        ).all()
        user_ids = [f.requester_id if f.requester_id != user_id else f.receiver_id for f in accepted]
        return User.query.filter(User.id.in_(user_ids)).all()

    def is_online(user):
        if not user.last_seen:
            return False
        return (datetime.utcnow() - user.last_seen).total_seconds() < 300
    
    def last_seen_human(self):
        if not self.last_seen:
            return "Нет данных"
        now = datetime.utcnow()
        delta = now - self.last_seen
        if delta < timedelta(minutes=5):
            return "В сети"
        elif self.last_seen.date() == now.date():
            return "Сегодня"
        elif self.last_seen.date() == (now - timedelta(days=1)).date():
            return "Вчера"
        else:
            return f"{delta.days} дн. назад"

class SocialLinks(db.Model):
    __tablename__ = 'social_links'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    telegram = db.Column(db.String(128))
    discord = db.Column(db.String(128))
    steam = db.Column(db.String(128))


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_updated = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    topic = db.Column(db.String(64), nullable=True)
    roadmap_key = db.Column(db.String(64), nullable=True)  # новое поле — связь с roadmap
    is_published = db.Column(db.Boolean, default=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='blog_posts')

    def __repr__(self):
        return f"<BlogPost('{self.title}', '{self.date_created}')>"


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    # Уведомления
    notif_email_forum = db.Column(db.Boolean, default=True)
    notif_email_comments = db.Column(db.Boolean, default=True)
    notif_email_updates = db.Column(db.Boolean, default=True)
    notif_push_forum = db.Column(db.Boolean, default=True)
    notif_push_comments = db.Column(db.Boolean, default=True)
    notif_push_updates = db.Column(db.Boolean, default=True)

    # Приватность
    profile_privacy = db.Column(db.String(20), default='public')  # public | friends | private

    # Тема
    theme = db.Column(db.String(10), default='light')  # light | dark | neon | cyberpunk


class RoadmapItem(db.Model):
    __tablename__ = 'roadmap_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)      # Название этапа (как на сайте)
    roadmap_key = db.Column(db.String(64), nullable=False) # Привязанный topic из BlogPost
    goal_posts = db.Column(db.Integer, nullable=False)     # Сколько постов нужно для 100%


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending | accepted | declined

    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')
