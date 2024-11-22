from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Shop
from app import db
from datetime import datetime

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.player'))

    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        shop = Shop.query.filter_by(shop_name=shop_name).first()

        if shop and shop.check_password(password):
            login_user(shop, remember=remember)
            # Update last login time
            shop.last_login = datetime.now()
            db.session.commit()

            next_page = request.args.get('next')
            if shop.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('main.player'))

        flash('Invalid username or password', 'error')
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))