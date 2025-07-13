import os
import uuid
from sqlalchemy import func, or_
from werkzeug.utils import secure_filename
from flask import Blueprint, current_app, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError
from . import csrf
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import *
from .models import *
from . import db, bcrypt
from app import models


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

@main.route("/blog")
def blog():
    query = BlogPost.query.join(User)

    # Фильтры
    search = request.args.get('q', '').strip().lower()
    topic = request.args.get('topic', '').strip()
    roadmap_key = request.args.get('roadmap_key', '').strip()
    date = request.args.get('date', '').strip()

    if search:
        query = query.filter(or_(
            func.lower(BlogPost.title).like(f"%{search}%"),
            func.lower(BlogPost.content).like(f"%{search}%")
        ))

    if topic:
        query = query.filter(BlogPost.topic == topic)

    if roadmap_key:
        query = query.filter(BlogPost.roadmap_key == roadmap_key)

    if date:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(func.date(BlogPost.date_created) == date_obj.date())
        except ValueError:
            pass  

    posts = query.order_by(BlogPost.date_created.desc()).all()

    return render_template("blog.html", posts=posts, search=search, topic=topic, roadmap_key=roadmap_key, date=date)

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            topic=form.topic.data,
            roadmap_key=form.roadmap_key.data or None,
            author=current_user
        )
        db.session.add(post)

        if form.roadmap_key.data:
            existing_item = RoadmapItem.query.filter_by(roadmap_key=form.roadmap_key.data).first()
            if not existing_item:
                new_item = RoadmapItem(
                    title=form.title.data,
                    roadmap_key=form.roadmap_key.data,
                    goal_posts=11 
                )
                db.session.add(new_item)

        db.session.commit()
        flash("Пост успешно создан!", "success")
        return redirect(url_for('main.blog'))

    return render_template('create_post.html', form=form)

@main.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/easteregg')
def easteregg():
    return render_template('easteregg.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()
    social_form = SocialLinksForm(obj=current_user.social_links or SocialLinks())
    
    friends_count = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) | 
         (Friendship.receiver_id == current_user.id)) &
        (Friendship.status == 'accepted')
    ).cou

    if 'save_profile' in request.form and profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data

        # Загрузка аватара
        if profile_form.avatar.data:
            if profile_form.avatar.data.mimetype not in ['image/jpeg', 'image/png']:
                flash('Файл должен быть изображением PNG или JPG', 'danger')
                return redirect(url_for('main.profile'))

            filename = secure_filename(profile_form.avatar.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"

            avatar_folder = os.path.join(current_app.root_path, 'static', 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)

            avatar_path = os.path.join(avatar_folder, unique_filename)

            # Только один вызов save()
            profile_form.avatar.data.save(avatar_path)

            # Проверка успешности
            if not os.path.exists(avatar_path):
                print("❌ Файл не создан!")
            else:
                print("✅ Файл создан!", os.path.abspath(avatar_path))

            # Относительный путь для отображения через Flask
            current_user.avatar = f"avatars/{unique_filename}"


        db.session.commit()
        flash('Профиль обновлён', 'success')
        return redirect(url_for('main.profile'))

    elif 'change_password' in request.form and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Текущий пароль неверен', 'danger')
        elif password_form.current_password.data == password_form.new_password.data:
            flash('Новый пароль совпадает с текущим', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменён', 'success')
            return redirect(url_for('main.profile'))

    elif 'save_socials' in request.form and social_form.validate_on_submit():
        if current_user.social_links:
            current_user.social_links.telegram = social_form.telegram.data
            current_user.social_links.discord = social_form.discord.data
            current_user.social_links.steam = social_form.steam.data
        else:
            new_links = SocialLinks(
                user=current_user,
                telegram=social_form.telegram.data,
                discord=social_form.discord.data,
                steam=social_form.steam.data
            )
            db.session.add(new_links)
        db.session.commit()
        flash('Соцсети обновлены', 'success')
        return redirect(url_for('main.profile'))

    # Инициализация значений
    profile_form.username.data = current_user.username
    profile_form.email.data = current_user.email
    if current_user.social_links:
        social_form.telegram.data = current_user.social_links.telegram
        social_form.discord.data = current_user.social_links.discord
        social_form.steam.data = current_user.social_links.steam

    return render_template(
        'profile.html',
        profile_form=profile_form,
        password_form=password_form,
        social_form=social_form,
        user=current_user,
        friends_count=friends_count 
    )

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
    
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        if not current_user.settings:
            current_user.settings = UserSettings(user=current_user)

        # Обновляем значения
        current_user.settings.notif_email_forum = form.notif_email_forum.data
        current_user.settings.notif_email_comments = form.notif_email_comments.data
        current_user.settings.notif_email_updates = form.notif_email_updates.data
        current_user.settings.notif_push_forum = form.notif_push_forum.data
        current_user.settings.notif_push_comments = form.notif_push_comments.data
        current_user.settings.notif_push_updates = form.notif_push_updates.data
        current_user.settings.profile_privacy = form.profile_privacy.data
        current_user.settings.theme = form.theme.data

        db.session.commit()
        flash("Настройки обновлены", "success")
        return redirect(url_for('main.settings'))

    # Заполняем форму текущими данными
    if current_user.settings:
        form.notif_email_forum.data = current_user.settings.notif_email_forum
        form.notif_email_comments.data = current_user.settings.notif_email_comments
        form.notif_email_updates.data = current_user.settings.notif_email_updates
        form.notif_push_forum.data = current_user.settings.notif_push_forum
        form.notif_push_comments.data = current_user.settings.notif_push_comments
        form.notif_push_updates.data = current_user.settings.notif_push_updates
        form.profile_privacy.data = current_user.settings.profile_privacy
        form.theme.data = current_user.settings.theme

    form.theme.data = current_user.settings.theme
    
    return render_template('settings.html', form=form)

@main.context_processor
def inject_theme():
    if current_user.is_authenticated and current_user.settings:
        return dict(theme=current_user.settings.theme or 'dark')
    return dict(theme='dark')

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

@main.route('/search', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    users = []

    if query:
        users = User.query.filter(
            or_(
                User.username.ilike(f"%{query}%")
            )
        ).filter(User.id != current_user.id).all()
 
    # 👉 Только после получения users — выполняем запрос на дружбу
    user_ids = [u.id for u in users]
    existing_friendships = Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == current_user.id, Friendship.receiver_id.in_(user_ids)),
            and_(Friendship.receiver_id == current_user.id, Friendship.requester_id.in_(user_ids))
        )
    ).all()

    # Словарь статусов
    friend_status = {}
    for f in existing_friendships:
        other_id = f.receiver_id if f.requester_id == current_user.id else f.requester_id
        friend_status[other_id] = f.status

    return render_template('search.html', users=users, query=query, friend_status=friend_status)

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('main.index'))
    return render_template('admin.html')

@main.route('/roadmap')
def roadmap():
    roadmap_items = RoadmapItem.query.all()
    progress_data = {}

    for item in roadmap_items:
        count = BlogPost.query.filter_by(roadmap_key=item.roadmap_key).count()
        progress = min(int((count / item.goal_posts) * 100), 100) if item.goal_posts > 0 else 0
        print(f"Roadmap Key: {item.roadmap_key}, Count: {count}, Goal: {item.goal_posts}, Progress: {progress}")

        progress_data[item.roadmap_key] = {
            "label": item.title,
            "progress": progress
        }

    return render_template('roadmap.html', progress_data=progress_data)

@main.route("/friends")
@login_required
def friends():
    # Принятые
    friends = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) | (Friendship.receiver_id == current_user.id)) &
        (Friendship.status == 'accepted')
    ).all()

    # Полученные заявки
    incoming = Friendship.query.filter_by(receiver_id=current_user.id, status='pending').all()

    # Отправленные заявки
    outgoing = Friendship.query.filter_by(requester_id=current_user.id, status='pending').all()

    return render_template('friends.html', friends=friends, incoming=incoming, outgoing=outgoing)

@main.route("/friends/request/<int:user_id>", methods=['POST'])
@login_required
def send_friend_request(user_id):
    form = EmptyForm()    
    if user_id == current_user.id:
        flash("Нельзя добавить себя в друзья", "warning")
        return redirect(request.referrer or url_for('main.index'))

    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_requests = Friendship.query.filter(
        Friendship.requester_id == current_user.id,
        Friendship.created_at >= last_24h
    ).count()
    
    if recent_requests >= 5:
        flash("Лимит: 5 заявок в сутки", "danger")
        return redirect(request.referrer or url_for('main.index'))

    existing = Friendship.query.filter_by(
        requester_id=current_user.id,
        receiver_id=user_id
    ).first()

    if existing:
        flash("Заявка уже отправлена", "info")
        return redirect(request.referrer or url_for('main.index'))

    new_request = Friendship(
        requester_id=current_user.id, 
        receiver_id=user_id, 
        status='pending')
    
    db.session.add(new_request)
    db.session.commit()
    flash("Заявка отправлена", "success")
    return redirect(request.referrer or url_for('main.index'))


@main.route("/friends/accept/<int:friendship_id>", methods=['POST'])
@login_required
def accept_friend_request(friendship_id):
    form = EmptyForm()    
    fs = Friendship.query.get_or_404(friendship_id)
    if fs.receiver_id != current_user.id:
        flash("Вы не можете подтвердить эту заявку", "danger")
        return redirect(url_for('main.friends'))

    fs.status = 'accepted'
    db.session.commit()
    flash("Заявка принята", "success")
    return redirect(url_for('main.friends'))

@main.route("/friends/cancel/<int:friendship_id>", methods=['POST'])
@login_required
def cancel_friend_request(friendship_id):
    form = EmptyForm()
    print(f"DEBUG: Cancel request for friendship_id={friendship_id}")  # Логирование
    
    fs = Friendship.query.get_or_404(friendship_id)
    print(f"DEBUG: Found friendship: {fs.id}, requester={fs.requester_id}, receiver={fs.receiver_id}")

    if fs.requester_id != current_user.id:
        print("DEBUG: User is not the requester! Access denied.")
        flash("Вы не можете отменить эту заявку", "danger")
        return redirect(url_for('main.friends'))

    db.session.delete(fs)
    db.session.commit()
    print("DEBUG: Friendship deleted successfully.")
    flash("Заявка отменена", "info")
    return redirect(url_for('main.friends'))

@main.route("/friends/remove/<int:user_id>", methods=['POST'])
@login_required
def remove_friend(user_id):
    fs = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.receiver_id == user_id)) |
        ((Friendship.receiver_id == current_user.id) & (Friendship.requester_id == user_id)),
        Friendship.status == 'accepted'
    ).first()
    if fs:
        db.session.delete(fs)
        db.session.commit()
        flash("Пользователь удалён из друзей", "info")
    else:
        flash("Вы не в друзьях", "warning")
    empty_form = EmptyForm()
    return redirect(url_for('main.friends'))

@main.route('/api/friends/status')
@login_required
def friends_status():
    friends = User.get_friends_for_user(current_user.id)
    response = []
    for friend in friends:
        if User.is_online(friend):
            status = '🟢 Онлайн'
        else:
            status = f'🔴 Оффлайн, был(а): {friend.last_seen_human()}'
        response.append({'username': friend.username, 'status': status})
    return jsonify(response)

@main.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
