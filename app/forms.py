from flask_wtf import FlaskForm
from wtforms import BooleanField, RadioField, SelectField, StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя')
    email = StringField('Email')
    avatar = FileField('Аватар')
    submit = SubmitField('Сохранить изменения') 

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Сменить пароль') 

class SocialLinksForm(FlaskForm):
    telegram = StringField('Telegram')
    discord = StringField('Discord')
    steam = StringField('Steam')
    submit = SubmitField('Сохранить') 

class BlogPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=128)])
    topic = SelectField("Категория", choices=[
        ("Обновления", "Обновления"),
        ("Технологии", "Технологии"),
        ("События", "События")
    ], validators=[DataRequired()])

    roadmap_key = SelectField("Этап Roadmap (опционально)", choices=[
        ("", "— не связано —"),
        ("site_beta", "📦 Бета-версия сайта"),
        ("ai_playground", "🧠 AI Playground + визуализация"),
        ("game_portal", "🎮 Игровой портал и WebGL-галерея"),
        ("interactive_blog", "💬 Интерактивный блог + Easter Eggs"),
        ("cms_modular", "⚙️ CMS и модульная архитектура"),
        ("mini_game", "🚀 Релиз первой мини-игры"),
        ("launcher_pwa", "🌌 Лаунчер и PWA-функции"),
    ], validators=[Optional()])

    content = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class SettingsForm(FlaskForm):
    # Уведомления
    notif_email_forum = BooleanField("Email: новые сообщения на форуме")
    notif_email_comments = BooleanField("Email: ответы на комментарии")
    notif_email_updates = BooleanField("Email: обновления игр")
    notif_push_forum = BooleanField("Push-уведомления: новые сообщения на форуме")
    notif_push_comments = BooleanField("Push-уведомления: ответы на комментарии")
    notif_push_updates = BooleanField("Push-уведомления: обновления игр")

    # Приватность
    profile_privacy = RadioField("Приватность", choices=[
        ("public", "Профиль виден всем"),
        ("friends", "Виден только для друзей"),
        ("private", "Профиль закрыт")
    ], validators=[DataRequired()])

    # Тема
    theme = RadioField(choices=[
        ('light', 'Светлая'),
        ('dark', 'Тёмная'),
        ('neon', 'Неоновая'),
        ('cyber', 'Киберпанк')
    ], validators=[DataRequired()])

    submit = SubmitField("Сохранить настройки")

class EmptyForm(FlaskForm):
    """Пустая форма — только для CSRF."""
    pass