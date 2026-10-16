from datetime import datetime
from flask import jsonify, request
from flask_login import current_user, login_required
from flask_babel import _
from app.api import bp
from app import db
from app.models import Event, Quiz, QuestionGroup, Question, Answer, QuizAttempt, Team, User

@bp.route('/events/<int:event_id>/quiz', methods=['GET'])
@login_required
def get_quiz_data(event_id):
    """Retrieve full quiz structure, groups, questions, settings, and user progress."""
    event = Event.query.get_or_404(event_id)
    if not event.is_active:
        return jsonify({'error': _('Event is not active')}), 400
    
    if not current_user.team_id:
        return jsonify({'error': _('You must join a team first')}), 400
    
    quiz = event.quiz
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if not attempt:
        attempt = QuizAttempt(user_id=current_user.id, event_id=event.id, current_group_index=0, highest_group_index=0)
        db.session.add(attempt)
        db.session.commit()
    
    # Fetch groups
    groups = QuestionGroup.query.filter_by(quiz_id=quiz.id).order_by(QuestionGroup.order).all()
    all_questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order).all()
    
    # If no groups defined, create a virtual single group
    if not groups:
        group_list = [{
            'id': None,
            'name': _('Questions'),
            'description': '',
            'order': 0,
            'allow_backtrack': True,
            'questions': []
        }]
    else:
        group_list = []
        for g in groups:
            group_list.append({
                'id': g.id,
                'name': g.name,
                'description': g.description or '',
                'order': g.order,
                'allow_backtrack': g.allow_backtrack,
                'questions': []
            })
    
    group_map = {}
    for g in group_list:
        gid = g.get('id')
        if gid is not None and isinstance(gid, int):
            group_map[gid] = g
    ungrouped = []
    
    user_answers = {a.question_id: a for a in Answer.query.filter_by(user_id=current_user.id).all()}
    
    for q in all_questions:
        ans = user_answers.get(q.id)
        q_data = {
            'id': q.id,
            'group_id': q.group_id,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'points': q.points,
            'order': q.order,
            'requires_review': q.requires_review,
            'answered': ans is not None,
            'user_answer': ans.selected_answer if ans else None,
        }
        
        # Immediate feedback visibility
        if ans and quiz.instant_feedback:
            q_data['is_correct'] = ans.is_correct
            q_data['points_earned'] = ans.points_earned
            q_data['is_reviewed'] = ans.is_reviewed
        
        if q.group_id is not None and q.group_id in group_map:
            group_map[q.group_id]['questions'].append(q_data)
        elif group_list and group_list[0]['id'] is None:
            group_list[0]['questions'].append(q_data)
        else:
            ungrouped.append(q_data)
            
    if ungrouped:
        if group_list and group_list[0]['id'] is None:
            group_list[0]['questions'].extend(ungrouped)
        else:
            group_list.append({
                'id': -1,
                'name': _('General Questions'),
                'description': '',
                'order': 999,
                'allow_backtrack': True,
                'questions': ungrouped
            })
            
    # Remove empty groups if any
    group_list = [g for g in group_list if len(g['questions']) > 0]
    if not group_list:
        group_list = [{
            'id': None,
            'name': _('Questions'),
            'description': '',
            'order': 0,
            'allow_backtrack': True,
            'questions': []
        }]

    team = current_user.team
    
    return jsonify({
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description or '',
            'instant_feedback': quiz.instant_feedback,
            'show_score_at_end': quiz.show_score_at_end,
            'show_correct_answers_at_end': quiz.show_correct_answers_at_end,
        },
        'event': {
            'id': event.id,
            'name': event.name,
            'description': event.description or '',
            'start_time': event.start_time.isoformat(),
            'end_time': event.end_time.isoformat(),
            'is_active': event.is_active,
        },
        'team': {
            'id': team.id if team else None,
            'name': team.name if team else '',
            'score': team.score if team else 0,
        },
        'attempt': {
            'is_completed': attempt.is_completed,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
            'current_group_index': attempt.current_group_index,
            'highest_group_index': attempt.highest_group_index,
        },
        'groups': group_list,
        'total_questions': len(all_questions),
        'answered_count': len([q for q in all_questions if q.id in user_answers])
    })

@bp.route('/quiz/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit an answer to a question via API."""
    data = request.get_json() or request.form
    question_id = data.get('question_id')
    selected_answer = data.get('answer')
    
    if not question_id:
        return jsonify({'error': _('Question ID is required')}), 400
    
    question = Question.query.get_or_404(question_id)
    quiz = question.quiz
    
    # Check if already answered
    existing = Answer.query.filter_by(user_id=current_user.id, question_id=question_id).first()
    if existing:
        return jsonify({'error': _('You have already answered this question'), 'already_answered': True}), 400
    
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
        if isinstance(selected_answer, list):
            selected_answers = selected_answer
        elif isinstance(selected_answer, str):
            selected_answers = [a.strip() for a in selected_answer.split(',') if a.strip()]
        else:
            selected_answers = []
        selected_answer_str = ','.join(sorted(selected_answers))
        correct_answers = [a.strip() for a in question.correct_answer.split(',') if a.strip()] if question.correct_answer else []
        is_correct = set(selected_answers) == set(correct_answers)
        points_earned = question.points if is_correct else 0
        selected_answer = selected_answer_str
    else:
        # multiple_choice
        is_correct = (str(selected_answer).strip().lower() == str(question.correct_answer).strip().lower()) if question.correct_answer else False
        points_earned = question.points if is_correct else 0
    
    answer = Answer(
        user_id=current_user.id,
        question_id=question_id,
        selected_answer=str(selected_answer or ''),
        is_correct=is_correct,
        points_earned=points_earned,
        is_reviewed=not question.requires_review
    )
    db.session.add(answer)
    
    if is_correct and current_user.team:
        current_user.team.score += points_earned
    
    db.session.commit()
    
    resp = {
        'success': True,
        'question_id': question.id,
        'user_answer': answer.selected_answer,
        'team_score': current_user.team.score if current_user.team else 0
    }
    
    if quiz.instant_feedback:
        resp['is_correct'] = is_correct
        resp['points_earned'] = points_earned
        resp['requires_review'] = question.requires_review
        resp['message'] = _('Correct!') if is_correct else (_('Answer submitted! It will be reviewed manually.') if question.requires_review else _('Incorrect!'))
    else:
        resp['message'] = _('Answer saved!')
        
    return jsonify(resp)

@bp.route('/events/<int:event_id>/update_progress', methods=['POST'])
@login_required
def update_progress(event_id):
    """Update user's current group index during quiz navigation."""
    data = request.get_json() or {}
    group_index = data.get('group_index', 0)
    
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not attempt:
        attempt = QuizAttempt(user_id=current_user.id, event_id=event_id)
        db.session.add(attempt)
    
    attempt.current_group_index = group_index
    if group_index > attempt.highest_group_index:
        attempt.highest_group_index = group_index
    
    db.session.commit()
    return jsonify({'success': True, 'current_group_index': attempt.current_group_index, 'highest_group_index': attempt.highest_group_index})

@bp.route('/events/<int:event_id>/complete', methods=['POST'])
@login_required
def complete_quiz(event_id):
    """Mark quiz as completed for current user and calculate summary."""
    event = Event.query.get_or_404(event_id)
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not attempt:
        attempt = QuizAttempt(user_id=current_user.id, event_id=event_id)
        db.session.add(attempt)
    
    attempt.is_completed = True
    attempt.completed_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'completed_at': attempt.completed_at.isoformat()})

@bp.route('/events/<int:event_id>/results', methods=['GET'])
@login_required
def get_quiz_results(event_id):
    """Get final results and breakdown for the quiz."""
    event = Event.query.get_or_404(event_id)
    quiz = event.quiz
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order).all()
    user_answers = {a.question_id: a for a in Answer.query.filter_by(user_id=current_user.id).all()}
    
    total_points_possible = sum(q.points for q in questions)
    user_points_earned = sum(a.points_earned for a in user_answers.values())
    correct_count = sum(1 for a in user_answers.values() if a.is_correct)
    total_questions = len(questions)
    
    questions_summary = []
    for q in questions:
        ans = user_answers.get(q.id)
        q_item = {
            'id': q.id,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'points': q.points,
            'points_earned': ans.points_earned if ans else 0,
            'is_correct': ans.is_correct if ans else False,
            'is_reviewed': ans.is_reviewed if ans else True,
            'user_answer': ans.selected_answer if ans else None,
        }
        
        # Only show correct answers if quiz setting allows
        if quiz.show_correct_answers_at_end:
            if q.question_type == 'free_text':
                q_item['correct_answers'] = q.correct_answers.split('\n') if q.correct_answers else []
            elif q.question_type == 'multiple_select':
                q_item['correct_answer'] = q.correct_answer
            else:
                q_item['correct_answer'] = q.correct_answer
                
            q_item['option_a'] = q.option_a
            q_item['option_b'] = q.option_b
            q_item['option_c'] = q.option_c
            q_item['option_d'] = q.option_d
            
        questions_summary.append(q_item)
    
    return jsonify({
        'quiz_title': quiz.title,
        'event_name': event.name,
        'is_completed': attempt.is_completed if attempt else False,
        'show_score': quiz.show_score_at_end,
        'show_correct_answers': quiz.show_correct_answers_at_end,
        'total_questions': total_questions,
        'answered_count': len(user_answers),
        'correct_count': correct_count,
        'total_points_possible': total_points_possible,
        'user_points_earned': user_points_earned,
        'team_score': current_user.team.score if current_user.team else 0,
        'team_name': current_user.team.name if current_user.team else '',
        'percentage': round((user_points_earned / total_points_possible * 100), 1) if total_points_possible > 0 else 0,
        'questions': questions_summary
    })
