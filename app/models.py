import secrets
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_captain(self):
        if not self.team:
            return False
        return self.team.captain_id == self.id

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    max_size = db.Column(db.Integer, default=5)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref='teams')
    score = db.Column(db.Integer, default=0)
    captain_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    captain = db.relationship('User', foreign_keys=[captain_id], backref='captained_teams')
    invite_token = db.Column(db.String(64), unique=True, index=True, default=lambda: secrets.token_urlsafe(16))
    members = db.relationship('User', foreign_keys=[User.team_id], backref='team')

    def generate_invite_token(self):
        self.invite_token = secrets.token_urlsafe(16)
        return self.invite_token

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    quiz = db.relationship('Quiz', backref='events')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    instant_feedback = db.Column(db.Boolean, default=False)
    show_score_at_end = db.Column(db.Boolean, default=True)
    show_correct_answers_at_end = db.Column(db.Boolean, default=True)
    groups = db.relationship('QuestionGroup', backref='quiz', lazy='dynamic', cascade='all, delete-orphan', order_by='QuestionGroup.order')
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan', order_by='Question.order')

class QuestionGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    allow_backtrack = db.Column(db.Boolean, default=True)  # Can user navigate back to this/from next group?
    questions = db.relationship('Question', backref='group', lazy='dynamic', order_by='Question.order')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('question_group.id'), nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # 'multiple_choice', 'free_text', 'multiple_select'
    option_a = db.Column(db.String(256), nullable=True)
    option_b = db.Column(db.String(256), nullable=True)
    option_c = db.Column(db.String(256), nullable=True)
    option_d = db.Column(db.String(256), nullable=True)
    correct_answer = db.Column(db.Text, nullable=True)  # Can be 'a', 'b', 'c', 'd', or comma-separated for multiple
    correct_answers = db.Column(db.Text, nullable=True)  # JSON/Newline array of correct answers for free-text
    points = db.Column(db.Integer, default=10)
    order = db.Column(db.Integer, default=0)
    requires_review = db.Column(db.Boolean, default=False)  # For free-text questions needing manual review

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    current_group_index = db.Column(db.Integer, default=0)
    highest_group_index = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='quiz_attempts')
    event = db.relationship('Event', backref='quiz_attempts')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.Text, nullable=True)  # Changed to Text to support free-text
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_reviewed = db.Column(db.Boolean, default=False)  # For manual review
    review_comment = db.Column(db.Text, nullable=True)  # Admin comment on review
    user = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='answers')
