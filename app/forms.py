from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

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
    topic = SelectField("Тема", choices=[
        ("Обновления", "Обновления"),
        ("Технологии", "Технологии"),
        ("События", "События")
    ], validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')