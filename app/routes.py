from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm
from . import db

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
def profile():
    return render_template('profile.html')

@main.route('/register')
def register():
    return render_template('register.html')

@main.route('/login')
def login():
    return render_template('login.html')
    
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
def admin():
    if not request.args.get('admin'):
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))
    return render_template('admin.html')
