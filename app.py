import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Post, Comment
from forms import RegisterForm, LoginForm, PostForm, EditProfileForm
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AVATAR_FOLDER'] = 'static/avatars'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        avatar_file = form.avatar.data
        avatar_filename = None
        if avatar_file:
            avatar_filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join(app.config['AVATAR_FOLDER'], avatar_filename)
            avatar_file.save(avatar_path)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.avatar = avatar_filename
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Ваш аккаунт заблокирован.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверные имя пользователя или пароль.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        avatar_file = form.avatar.data
        if avatar_file:
            avatar_filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join(app.config['AVATAR_FOLDER'],
