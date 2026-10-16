from flask import render_template, redirect, url_for, request, session, g
from flask_login import current_user
from app.main import bp
from app.models import Event, Team, Quiz, User

@bp.route('/')
def index():
    # Landing page
    active_count = Event.query.filter_by(is_active=True).count()
    total_quizzes = Quiz.query.count()
    total_teams = Team.query.count()
    featured_events = Event.query.filter_by(is_active=True).limit(3).all()
    return render_template('landing.html', 
                           active_count=active_count, 
                           total_quizzes=total_quizzes, 
                           total_teams=total_teams,
                           featured_events=featured_events)

@bp.route('/events')
def events():
    active_events = Event.query.filter_by(is_active=True).all()
    past_events = Event.query.filter_by(is_active=False).order_by(Event.end_time.desc()).all()
    return render_template('events.html', active_events=active_events, past_events=past_events, events=active_events)

@bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['en', 'hu']:
        session['language'] = lang
        session.modified = True
        if hasattr(g, '_flask_babel'):
            delattr(g, '_flask_babel')
    referrer = request.referrer
    if referrer and '/set_language' not in referrer:
        return redirect(referrer)
    return redirect(url_for('main.index'))
