from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models import ButtonPress
from app import db
from sqlalchemy import func

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/player')
@login_required
def player():
    # Get view counts for current shop only
    counts = db.session.query(
        ButtonPress.button_number,
        func.count(ButtonPress.id)
    ).filter(
        ButtonPress.shop_id == current_user.id
    ).group_by(ButtonPress.button_number).all()

    count_dict = {btn: count for btn, count in counts}

    videos = [
        {
            'id': 1,
            'name': '55 inch UHD',
            'icon': 'fas fa-tv',
            'class': 'uhd-button',
            'count': count_dict.get(1, 0)
        },
        {
            'id': 2,
            'name': '55 Inch Mini LED',
            'icon': 'fas fa-digital-tachograph',
            'class': 'mini-led-button',
            'count': count_dict.get(2, 0)
        },
        {
            'id': 3,
            'name': '65 Inch Gaming QLED',
            'icon': 'fas fa-gamepad',
            'class': 'gaming-button',
            'count': count_dict.get(3, 0)
        },
        {
            'id': 4,
            'name': '65 Inch Mini LED',
            'icon': 'fas fa-crown',
            'class': 'premium-button',
            'count': count_dict.get(4, 0)
        }
    ]

    return render_template('player.html', videos=videos)

@main.route('/get_counts')
@login_required
def get_counts():
    # Get counts for current shop only
    counts = db.session.query(
        ButtonPress.button_number,
        func.count(ButtonPress.id)
    ).filter(
        ButtonPress.shop_id == current_user.id
    ).group_by(ButtonPress.button_number).all()

    return jsonify({btn: count for btn, count in counts})


@main.route('/log_play', methods=['POST'])
@login_required
def log_play():
    try:
        button_number = int(request.form.get('button_number'))
        new_press = ButtonPress(
            shop_id=current_user.id,
            button_number=button_number
        )
        db.session.add(new_press)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

