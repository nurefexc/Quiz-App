from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from functools import wraps
from app.admin import bp
from app.models import Quiz, Question, QuestionGroup, Event, Team, User
from app.admin.forms import QuizForm, QuestionForm, QuestionGroupForm, EventForm, TeamForm
from app import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash(_('Admin access required'))
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    quizzes = Quiz.query.all()
    events = Event.query.all()
    teams = Team.query.all()
    return render_template('admin/dashboard.html', quizzes=quizzes, events=events, teams=teams)

@bp.route('/quiz/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            instant_feedback=form.instant_feedback.data,
            show_score_at_end=form.show_score_at_end.data,
            show_correct_answers_at_end=form.show_correct_answers_at_end.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash(_('Quiz created successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz.id))
    return render_template('admin/create_quiz.html', form=form)

@bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.instant_feedback = form.instant_feedback.data
        quiz.show_score_at_end = form.show_score_at_end.data
        quiz.show_correct_answers_at_end = form.show_correct_answers_at_end.data
        db.session.commit()
        flash(_('Quiz updated successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz.id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    groups = QuestionGroup.query.filter_by(quiz_id=quiz_id).order_by(QuestionGroup.order).all()
    return render_template('admin/edit_quiz.html', quiz=quiz, questions=questions, groups=groups, form=form)

@bp.route('/quiz/<int:quiz_id>/group/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_group(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionGroupForm()
    if form.validate_on_submit():
        group_count = QuestionGroup.query.filter_by(quiz_id=quiz_id).count()
        group = QuestionGroup(
            quiz_id=quiz_id,
            name=form.name.data,
            description=form.description.data,
            allow_backtrack=form.allow_backtrack.data,
            order=group_count
        )
        db.session.add(group)
        db.session.commit()
        flash(_('Question group added successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    return render_template('admin/add_group.html', form=form, quiz=quiz)

@bp.route('/group/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_group(group_id):
    group = QuestionGroup.query.get_or_404(group_id)
    form = QuestionGroupForm(obj=group)
    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.allow_backtrack = form.allow_backtrack.data
        db.session.commit()
        flash(_('Question group updated successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=group.quiz_id))
    return render_template('admin/edit_group.html', form=form, group=group)

@bp.route('/group/<int:group_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_group(group_id):
    group = QuestionGroup.query.get_or_404(group_id)
    quiz_id = group.quiz_id
    # Unset group_id on associated questions so they are not lost
    Question.query.filter_by(group_id=group_id).update({'group_id': None})
    db.session.delete(group)
    db.session.commit()
    flash(_('Question group deleted'))
    return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))

@bp.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    groups = QuestionGroup.query.filter_by(quiz_id=quiz_id).order_by(QuestionGroup.order).all()
    form.group_id.choices = [(0, _('-- No Group (Default) --'))] + [(g.id, g.name) for g in groups]
    
    if form.validate_on_submit():
        question_count = Question.query.filter_by(quiz_id=quiz_id).count()
        selected_group = form.group_id.data if form.group_id.data and form.group_id.data > 0 else None
        question = Question(
            quiz_id=quiz_id,
            group_id=selected_group,
            question_text=form.question_text.data,
            question_type=form.question_type.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data,
            correct_answers=form.correct_answers.data,
            points=form.points.data,
            requires_review=form.requires_review.data,
            order=question_count
        )
        db.session.add(question)
        db.session.commit()
        flash(_('Question added successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
    return render_template('admin/add_question.html', form=form, quiz=quiz)

@bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash(_('Question deleted'))
    return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))

@bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    form = QuestionForm()
    groups = QuestionGroup.query.filter_by(quiz_id=question.quiz_id).order_by(QuestionGroup.order).all()
    form.group_id.choices = [(0, _('-- No Group (Default) --'))] + [(g.id, g.name) for g in groups]
    
    if form.validate_on_submit():
        question.group_id = form.group_id.data if form.group_id.data and form.group_id.data > 0 else None
        question.question_text = form.question_text.data
        question.question_type = form.question_type.data
        question.option_a = form.option_a.data
        question.option_b = form.option_b.data
        question.option_c = form.option_c.data
        question.option_d = form.option_d.data
        question.correct_answer = form.correct_answer.data
        question.correct_answers = form.correct_answers.data
        question.points = form.points.data
        question.requires_review = form.requires_review.data
        db.session.commit()
        flash(_('Question updated successfully'))
        return redirect(url_for('admin.edit_quiz', quiz_id=question.quiz_id))
    
    # Pre-fill form with existing data
    form.group_id.data = question.group_id or 0
    form.question_text.data = question.question_text
    form.question_type.data = question.question_type
    form.option_a.data = question.option_a
    form.option_b.data = question.option_b
    form.option_c.data = question.option_c
    form.option_d.data = question.option_d
    form.correct_answer.data = question.correct_answer
    form.correct_answers.data = question.correct_answers
    form.points.data = question.points
    form.requires_review.data = question.requires_review
    
    return render_template('admin/edit_question.html', form=form, question=question)

@bp.route('/quiz/<int:quiz_id>/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_questions(quiz_id):
    data = request.get_json() or {}
    question_ids = data.get('question_ids', [])
    
    for index, q_id in enumerate(question_ids):
        question = db.session.get(Question, q_id)
        if question and question.quiz_id == quiz_id:
            question.order = index
    
    db.session.commit()
    return {'success': True}

@bp.route('/event/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()
    form.quiz_id.choices = [(q.id, q.title) for q in Quiz.query.all()]
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            quiz_id=form.quiz_id.data
        )
        db.session.add(event)
        db.session.commit()
        flash(_('Event created successfully'))
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_event.html', form=form)

@bp.route('/event/<int:event_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_active = not event.is_active
    db.session.commit()
    if event.is_active:
        flash(_('Event activated'))
    else:
        flash(_('Event deactivated'))
    return redirect(url_for('admin.dashboard'))

@bp.route('/team/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_team():
    form = TeamForm()
    form.event_id.choices = [(e.id, e.name) for e in Event.query.all()]
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            max_size=form.max_size.data,
            event_id=form.event_id.data
        )
        db.session.add(team)
        db.session.commit()
        flash(_('Team created successfully'))
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_team.html', form=form)

@bp.route('/team/<int:team_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash(_('Team deleted'))
    return redirect(url_for('admin.dashboard'))
