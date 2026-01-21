from flask import render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from models import User, Post
from . import statistics_bp

def admin_required(f):
    from functools import wraps
    from flask import redirect, url_for, flash
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Доступ запрещён.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@statistics_bp.route('/stats')
@login_required
@admin_required
def admin_stats():
    cutoff = datetime.utcnow() - timedelta(days=7)

    stats = {
        'total_users': User.query.count(),
        'total_posts': Post.query.count(),
        'active_users': db.session.query(User).join(Post).distinct().count(),
        'banned_users': User.query.filter_by(is_banned=True).count(),
        'recent_posts': Post.query.filter(Post.timestamp >= cutoff).count()
    }

    return render_template('admin_stats.html', stats=stats)
