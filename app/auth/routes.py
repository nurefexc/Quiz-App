from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.auth import bp
from app.models import User, Team
from app.auth.forms import LoginForm, RegistrationForm
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login', next=request.args.get('next')))
        login_user(user, remember=form.remember_me.data)
        
        # Check if there is a pending team invite in session
        invite_token = session.pop('pending_invite_token', None)
        if invite_token:
            return redirect(url_for('quiz.team_invite', token=invite_token))
            
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registration successful'))
        
        # If there was an invite token, log in immediately and join
        invite_token = session.pop('pending_invite_token', None)
        if invite_token:
            login_user(user)
            return redirect(url_for('quiz.team_invite', token=invite_token))
            
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
