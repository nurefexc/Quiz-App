import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Quiz, Question, Event, Team, Answer, QuestionGroup, QuizAttempt
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Seed test data
        admin = User(username='admin', email='admin@test.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)

        user1 = User(username='user1', email='user1@test.com', is_admin=False)
        user1.set_password('user123')
        db.session.add(user1)

        user2 = User(username='user2', email='user2@test.com', is_admin=False)
        user2.set_password('user123')
        db.session.add(user2)

        user3 = User(username='user3', email='user3@test.com', is_admin=False)
        user3.set_password('user123')
        db.session.add(user3)

        quiz = Quiz(title='General Quiz', description='A test quiz', instant_feedback=True)
        db.session.add(quiz)
        db.session.flush()

        group = QuestionGroup(quiz_id=quiz.id, name='Group 1', order=0)
        db.session.add(group)
        db.session.flush()

        q1 = Question(
            quiz_id=quiz.id,
            group_id=group.id,
            question_text='What is 2+2?',
            question_type='multiple_choice',
            option_a='3', option_b='4', option_c='5', option_d='6',
            correct_answer='b',
            points=10,
            order=0
        )
        q2 = Question(
            quiz_id=quiz.id,
            group_id=group.id,
            question_text='Capital of Hungary?',
            question_type='free_text',
            correct_answers='Budapest\nbp',
            points=15,
            order=1
        )
        q3 = Question(
            quiz_id=quiz.id,
            group_id=group.id,
            question_text='Select prime numbers',
            question_type='multiple_select',
            option_a='2', option_b='3', option_c='4', option_d='6',
            correct_answer='a,b',
            points=10,
            order=2
        )
        q4 = Question(
            quiz_id=quiz.id,
            group_id=group.id,
            question_text='Manual review question',
            question_type='free_text',
            requires_review=True,
            points=20,
            order=3
        )
        db.session.add_all([q1, q2, q3, q4])

        active_event = Event(
            name='Active Test Event',
            description='Test event desc',
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            quiz_id=quiz.id,
            is_active=True
        )
        db.session.add(active_event)
        
        past_event = Event(
            name='Past Concluded Event',
            description='Concluded past event',
            start_time=datetime.now() - timedelta(days=30),
            end_time=datetime.now() - timedelta(days=20),
            quiz_id=quiz.id,
            is_active=False
        )
        db.session.add(past_event)
        db.session.flush()

        team_past = Team(name='Past Champions', max_size=5, event_id=past_event.id, score=120)
        db.session.add(team_past)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)

def test_index_page_and_past_events(client):
    # Test Landing page on root /
    response = client.get('/')
    assert response.status_code == 200
    assert 'Test Your Knowledge' in response.text or 'Quiz App' in response.text
    assert 'Active Test Event' in response.text

    # Test Events page on /events
    events_res = client.get('/events')
    assert events_res.status_code == 200
    assert 'Active Test Event' in events_res.text
    assert 'Past Concluded Event' in events_res.text
    assert 'Past Champions' in events_res.text
    assert 'Quiz App' in events_res.text

def test_language_switch(client):
    res = client.get('/set_language/hu', follow_redirects=True)
    assert res.status_code == 200
    assert 'Főoldal' in res.text

    res = client.get('/set_language/en', follow_redirects=True)
    assert res.status_code == 200
    assert 'Home' in res.text

def test_auth_flows(client):
    # Register existing username fails validation
    res = client.post('/auth/register', data={
        'username': 'user1',
        'email': 'diff@test.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert 'user1' in res.text

    # Register new user
    res = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200

    # Invalid login
    res = login(client, 'newuser', 'wrongpass')
    assert res.status_code == 200
    assert 'Invalid username or password' in res.text or 'Érvénytelen' in res.text

    # Valid login
    res = login(client, 'newuser', 'password123')
    assert res.status_code == 200
    assert 'newuser' in res.text

    # Logout
    res = client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200

def test_captain_team_registration_and_invite_flow(client, app):
    # 1. user1 creates a team and becomes captain
    login(client, 'user1', 'user123')
    res = client.post('/quiz/event/1/team/create', data={
        'name': 'Team Lightning',
        'max_size': 3
    }, follow_redirects=True)
    assert res.status_code == 200
    assert 'Team Lightning' in res.text
    assert 'Captain' in res.text or 'Team Captain' in res.text

    # Check team in database
    with app.app_context():
        u1 = User.query.filter_by(username='user1').first()
        team = Team.query.filter_by(name='Team Lightning').first()
        assert team is not None
        assert team.captain_id == u1.id
        assert u1.team_id == team.id
        assert u1.is_captain is True
        token = team.invite_token
        assert token is not None

    # 2. user2 visits the invite link and joins
    client.get('/auth/logout')
    login(client, 'user2', 'user123')
    
    invite_res = client.get(f'/quiz/team/invite/{token}', follow_redirects=True)
    assert invite_res.status_code == 200
    assert 'Team Lightning' in invite_res.text

    with app.app_context():
        u2 = User.query.filter_by(username='user2').first()
        assert u2.team_id == team.id
        assert u2.is_captain is False

    # 3. user2 cannot join another team or create another team while in Team Lightning
    dup_res = client.post('/quiz/event/1/team/create', data={
        'name': 'Another Team',
        'max_size': 3
    }, follow_redirects=True)
    assert dup_res.status_code == 200
    assert 'already in a team' in dup_res.text.lower() or 'már tagja' in dup_res.text.lower()

    # 4. Captain (user1) kicks member (user2)
    client.get('/auth/logout')
    login(client, 'user1', 'user123')
    
    with app.app_context():
        u2_id = User.query.filter_by(username='user2').first().id
        team_id = team.id

    kick_res = client.post(f'/quiz/team/{team_id}/remove_member/{u2_id}', follow_redirects=True)
    assert kick_res.status_code == 200

    with app.app_context():
        u2_after = User.query.filter_by(username='user2').first()
        assert u2_after.team_id is None

    # 5. Member leaves team
    # user3 joins via invite
    client.get('/auth/logout')
    login(client, 'user3', 'user123')
    client.get(f'/quiz/team/invite/{token}', follow_redirects=True)
    
    with app.app_context():
        u3 = User.query.filter_by(username='user3').first()
        assert u3.team_id == team_id

    leave_res = client.post(f'/quiz/team/{team_id}/leave', follow_redirects=True)
    assert leave_res.status_code == 200

    with app.app_context():
        u3_after = User.query.filter_by(username='user3').first()
        assert u3_after.team_id is None

def test_quiz_answering(client, app):
    # Setup team for user1
    login(client, 'user1', 'user123')
    client.post('/quiz/event/1/team/create', data={
        'name': 'Quizzer Team',
        'max_size': 3
    }, follow_redirects=True)

    # Start quiz
    res = client.get('/quiz/event/1/start')
    assert res.status_code == 200
    assert 'quiz-app-container' in res.text

    # Submit correct multiple choice answer
    res = client.post('/quiz/submit_answer', data={
        'question_id': '1',
        'answer': 'b'
    }, headers={'Referer': '/quiz/event/1/start'}, follow_redirects=True)
    assert res.status_code == 200
    assert 'Correct' in res.text or 'Helyes' in res.text

    # Submit free text answer (case insensitive match)
    res = client.post('/quiz/submit_answer', data={
        'question_id': '2',
        'answer': 'budapest'
    }, headers={'Referer': '/quiz/event/1/start'}, follow_redirects=True)
    assert res.status_code == 200

    # Submit multiple select answer
    res = client.post('/quiz/submit_answer', data={
        'question_id': '3',
        'answer': ['a', 'b']
    }, headers={'Referer': '/quiz/event/1/start'}, follow_redirects=True)
    assert res.status_code == 200

    # Submit manual review question
    res = client.post('/quiz/submit_answer', data={
        'question_id': '4',
        'answer': 'Some creative answer'
    }, headers={'Referer': '/quiz/event/1/start'}, follow_redirects=True)
    assert res.status_code == 200
    assert 'reviewed manually' in res.text.lower() or 'felülvizsgálat' in res.text.lower()

def test_admin_dashboard_and_crud(client):
    login(client, 'admin', 'admin123')
    
    # Dashboard
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert 'Admin Dashboard' in res.text or 'Vezérlőpult' in res.text

    # Create Quiz
    res = client.post('/admin/quiz/create', data={
        'title': 'Science Quiz',
        'description': 'Physics and Chemistry',
        'instant_feedback': True,
        'show_score_at_end': True,
        'show_correct_answers_at_end': True
    }, follow_redirects=True)
    assert res.status_code == 200
    assert 'Science Quiz' in res.text

    # Add Question to quiz 2
    res = client.post('/admin/quiz/2/question/add', data={
        'question_text': 'What is H2O?',
        'question_type': 'multiple_choice',
        'option_a': 'Water',
        'option_b': 'Air',
        'option_c': 'Earth',
        'option_d': 'Fire',
        'correct_answer': 'a',
        'points': 10
    }, follow_redirects=True)
    assert res.status_code == 200
    assert 'What is H2O?' in res.text

    # Delete Question
    res = client.post('/admin/question/5/delete', follow_redirects=True)
    assert res.status_code == 200

def test_standalone_frontend_and_custom_icons(client):
    # Verify index page renders with local css and js
    res = client.get('/')
    assert res.status_code == 200
    assert '/static/css/style.css' in res.text
    assert '/static/js/quiz.js' in res.text
    # Verify no external CDN scripts or stylesheets
    assert 'cdn.jsdelivr.net' not in res.text
    assert 'cdnjs.cloudflare.com' not in res.text
    assert 'unpkg.com' not in res.text

    # Verify custom SVG icons are served
    for icon in ['crown.svg', 'link.svg', 'trophy.svg', 'users.svg', 'user-minus.svg', 'log-out.svg', 'calendar.svg', 'copy.svg']:
        icon_res = client.get(f'/static/icons/{icon}')
        assert icon_res.status_code == 200
        assert '<svg' in icon_res.text

def test_api_quiz_endpoints_and_groups(client):
    login(client, 'user2', 'user123')
    
    # Create team
    client.post('/quiz/event/1/team/create', data={'name': 'API Testers', 'max_size': 5}, follow_redirects=True)
    
    # 1. Test GET /api/events/1/quiz
    res = client.get('/api/events/1/quiz')
    assert res.status_code == 200
    data = res.json
    assert 'quiz' in data
    assert 'groups' in data
    assert data['total_questions'] == 4

    # 2. Test POST /api/quiz/submit_answer
    res = client.post('/api/quiz/submit_answer', 
                      data=json.dumps({'question_id': 1, 'answer': 'b'}),
                      content_type='application/json')
    assert res.status_code == 200
    submit_data = res.json
    assert submit_data['success'] is True

    # 3. Test duplicate submission prevention
    res_dup = client.post('/api/quiz/submit_answer', 
                          data=json.dumps({'question_id': 1, 'answer': 'b'}),
                          content_type='application/json')
    assert res_dup.status_code == 400
    assert res_dup.json.get('already_answered') is True

    # 4. Test POST /api/events/1/update_progress
    res_prog = client.post('/api/events/1/update_progress',
                           data=json.dumps({'group_index': 1}),
                           content_type='application/json')
    assert res_prog.status_code == 200
    assert res_prog.json['current_group_index'] == 1

    # 5. Test POST /api/events/1/complete
    res_comp = client.post('/api/events/1/complete')
    assert res_comp.status_code == 200
    assert res_comp.json['success'] is True

    # 6. Test GET /api/events/1/results
    res_res = client.get('/api/events/1/results')
    assert res_res.status_code == 200
    assert res_res.json['is_completed'] is True
