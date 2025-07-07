from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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

    social_links = db.relationship('SocialLinks', backref='user', uselist=False)

    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}')>"

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
