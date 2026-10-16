from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from flask_babel import _
from app.quiz import bp
from app.models import Event, Team, Question, Answer, User, QuestionGroup, QuizAttempt
from app.quiz.forms import TeamCreateForm
from app import db

@bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    attempt = None
    if current_user.is_authenticated:
        attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    return render_template('quiz/event_detail.html', event=event, attempt=attempt)

@bp.route('/event/<int:event_id>/team/create', methods=['GET', 'POST'])
@login_required
def create_team(event_id):
    event = Event.query.get_or_404(event_id)
    if not event.is_active:
        flash(_('Event is not active'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    if current_user.team_id:
        flash(_('You are already in a team. You must leave your current team first.'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    form = TeamCreateForm()
    if form.validate_on_submit():
        existing_team = Team.query.filter_by(name=form.name.data, event_id=event_id).first()
        if existing_team:
            flash(_('A team with this name already exists for this event'))
            return render_template('quiz/create_team.html', form=form, event=event)
            
        team = Team(
            name=form.name.data,
            max_size=form.max_size.data,
            event_id=event_id,
            captain_id=current_user.id
        )
        db.session.add(team)
        db.session.flush() # Get team.id
        
        current_user.team_id = team.id
        db.session.commit()
        flash(_('Team registered successfully! You are the team captain.'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    return render_template('quiz/create_team.html', form=form, event=event)

@bp.route('/team/invite/<token>')
def team_invite(token):
    team = Team.query.filter_by(invite_token=token).first_or_404()
    event = team.event
    
    if not event.is_active:
        flash(_('This event is no longer active.'))
        return redirect(url_for('main.index'))
        
    if not current_user.is_authenticated:
        session['pending_invite_token'] = token
        flash(_('Please log in or register to join the team: %(team)s', team=team.name))
        return redirect(url_for('auth.login'))
        
    # User is logged in
    if current_user.team_id == team.id:
        flash(_('You are already a member of this team.'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    if current_user.team_id and current_user.team_id != team.id:
        flash(_('You are already in another team. You can only belong to one team at a time.'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    member_count = User.query.filter_by(team_id=team.id).count()
    if member_count >= team.max_size:
        flash(_('This team is already full.'))
        return redirect(url_for('quiz.event_detail', event_id=event.id))
        
    current_user.team_id = team.id
    db.session.commit()
    flash(_('You have successfully joined %(team)s!', team=team.name))
    return redirect(url_for('quiz.event_detail', event_id=event.id))

@bp.route('/team/<int:team_id>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id and not current_user.is_admin:
        flash(_('Only the team captain can remove members.'))
        return redirect(url_for('quiz.event_detail', event_id=team.event_id))
        
    if user_id == team.captain_id:
        flash(_('The captain cannot be removed from the team. Use leave team instead.'))
        return redirect(url_for('quiz.event_detail', event_id=team.event_id))
        
    target_user = User.query.get_or_404(user_id)
    if target_user.team_id != team.id:
        flash(_('User is not in this team.'))
        return redirect(url_for('quiz.event_detail', event_id=team.event_id))
        
    target_user.team_id = None
    db.session.commit()
    flash(_('Member %(username)s has been removed from the team.', username=target_user.username))
    return redirect(url_for('quiz.event_detail', event_id=team.event_id))

@bp.route('/team/<int:team_id>/regenerate_token', methods=['POST'])
@login_required
def regenerate_invite_token(team_id):
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id and not current_user.is_admin:
        flash(_('Only the team captain can regenerate the invite link.'))
        return redirect(url_for('quiz.event_detail', event_id=team.event_id))
        
    team.generate_invite_token()
    db.session.commit()
    flash(_('Invite link has been regenerated.'))
    return redirect(url_for('quiz.event_detail', event_id=team.event_id))

@bp.route('/team/<int:team_id>/join', methods=['POST'])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)
    flash(_('Joining teams is only possible via captain invite link.'))
    return redirect(url_for('quiz.event_detail', event_id=team.event_id))

@bp.route('/team/<int:team_id>/leave', methods=['POST'])
@login_required
def leave_team(team_id):
    team = Team.query.get_or_404(team_id)
    if current_user.team_id != team_id:
        flash(_('You are not in this team'))
        return redirect(url_for('main.index'))
    
    event_id = team.event_id
    current_user.team_id = None
    
    # If the user was captain:
    if team.captain_id == current_user.id:
        # Find another member
        remaining_member = User.query.filter_by(team_id=team.id).first()
        if remaining_member:
            team.captain_id = remaining_member.id
            flash(_('You left the team. Leadership has been transferred to %(user)s.', user=remaining_member.username))
        else:
            team.captain_id = None
            db.session.delete(team)
            flash(_('You left and dissolved the team.'))
    else:
        flash(_('Left team successfully'))
        
    db.session.commit()
    return redirect(url_for('quiz.event_detail', event_id=event_id))

@bp.route('/event/<int:event_id>/start')
@login_required
def start_quiz(event_id):
    event = Event.query.get_or_404(event_id)
    if not event.is_active:
        flash(_('Event is not active'))
        return redirect(url_for('quiz.event_detail', event_id=event_id))
    
    if not current_user.team_id:
        flash(_('You must join a team first'))
        return redirect(url_for('quiz.event_detail', event_id=event_id))
    
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if attempt and attempt.is_completed:
        return redirect(url_for('quiz.quiz_results', event_id=event_id))
        
    return render_template('quiz/quiz.html', event=event)

@bp.route('/event/<int:event_id>/results')
@login_required
def quiz_results(event_id):
    event = Event.query.get_or_404(event_id)
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    return render_template('quiz/results.html', event=event, attempt=attempt)

@bp.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    question_id = request.form.get('question_id')
    selected_answer = request.form.get('answer')
    
    question = Question.query.get_or_404(question_id)
    quiz = question.quiz
    
    # Check if already answered
    existing = Answer.query.filter_by(user_id=current_user.id, question_id=question_id).first()
    if existing:
        flash(_('You have already answered this question'))
        return redirect(request.referrer or url_for('main.index'))
    
    is_correct = False
    points_earned = 0
    
    if question.question_type == 'free_text':
        if question.requires_review:
            is_correct = False
            points_earned = 0
        else:
            correct_answers = [a.strip().lower() for a in question.correct_answers.split('\n') if a.strip()] if question.correct_answers else []
            selected_str = (selected_answer or '').strip().lower()
            is_correct = selected_str in correct_answers
            points_earned = question.points if is_correct else 0
    elif question.question_type == 'multiple_select':
        selected_answers = request.form.getlist('answer')
        selected_answer = ','.join(sorted(selected_answers))
        correct_answers = [a.strip() for a in question.correct_answer.split(',') if a.strip()] if question.correct_answer else []
        is_correct = set(selected_answers) == set(correct_answers)
        points_earned = question.points if is_correct else 0
    else:
        is_correct = (selected_answer == question.correct_answer)
        points_earned = question.points if is_correct else 0
    
    answer = Answer(
        user_id=current_user.id,
        question_id=question_id,
        selected_answer=selected_answer or '',
        is_correct=is_correct,
        points_earned=points_earned,
        is_reviewed=not question.requires_review
    )
    db.session.add(answer)
    
    if is_correct and current_user.team:
        current_user.team.score += points_earned
    
    db.session.commit()
    
    if quiz.instant_feedback:
        if question.requires_review:
            flash(_('Answer submitted! It will be reviewed manually.'))
        else:
            if is_correct:
                flash(_('Answer submitted! Correct'))
            else:
                flash(_('Answer submitted! Incorrect'))
    else:
        flash(_('Answer saved!'))
        
    return redirect(request.referrer or url_for('main.index'))
