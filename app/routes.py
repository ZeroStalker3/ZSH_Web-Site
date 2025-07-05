from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError
from . import csrf
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm
from .models import User
from . import db, bcrypt


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/games')
def games():
    return render_template('games.html')

@main.route('/blog')
def blog():
    return render_template('blog.html')

@main.route('/404')
def not_found():
    return render_template('404.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/easteregg')
def easteregg():
    return render_template('easteregg.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash('Пользователь с таким именем или email уже существует.', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
            return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.is_admin == True:
                login_user(user)
                flash('Вы вошли в систему.', 'success')
                return redirect(url_for('main.admin'))
            else:
                login_user(user)
                flash('Вы вошли в систему.', 'success')
                return redirect(url_for('main.profile'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('main.index'))
    
@main.route('/settings')
def settings():
    return render_template('settings.html')

@main.route('/shop')
def shop():
    return render_template('shop.html')

@main.route('/stats')
def stats():
    return render_template('stats.html')

@main.route('/jobs')
def jobs():
    return render_template('jobs.html')

@main.route('/builder')
def builder():
    return render_template('builder.html')

@main.route('/ThemesCustomizer')
def themes_customizer():
    return render_template('ThemesCustomizer.html')

@main.route('/search')
def search():
    return render_template('search.html')

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('main.index'))
    return render_template('admin.html')