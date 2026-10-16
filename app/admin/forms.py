from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional
from flask_babel import lazy_gettext as _l

class QuizForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'))
    instant_feedback = BooleanField(_l('Instant feedback on answers'), default=False)
    show_score_at_end = BooleanField(_l('Show score at quiz end'), default=True)
    show_correct_answers_at_end = BooleanField(_l('Show correct answers at quiz end'), default=True)
    submit = SubmitField(_l('Save Quiz'))

class QuestionGroupForm(FlaskForm):
    name = StringField(_l('Group Name'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    allow_backtrack = BooleanField(_l('Allow returning to previous group'), default=True)
    submit = SubmitField(_l('Save Group'))

class QuestionForm(FlaskForm):
    group_id = SelectField(_l('Question Group / Page'), coerce=int, validators=[Optional()])
    question_text = TextAreaField(_l('Question'), validators=[DataRequired()])
    question_type = SelectField(_l('Question Type'), choices=[
        ('multiple_choice', _l('Multiple Choice')),
        ('free_text', _l('Free Text')),
        ('multiple_select', _l('Multiple Select'))
    ], default='multiple_choice', validators=[DataRequired()])
    option_a = StringField(_l('Option A'), validators=[Optional()])
    option_b = StringField(_l('Option B'), validators=[Optional()])
    option_c = StringField(_l('Option C'), validators=[Optional()])
    option_d = StringField(_l('Option D'), validators=[Optional()])
    correct_answer = StringField(_l('Correct Answer (a,b,c,d or comma-separated)'), validators=[Optional()])
    correct_answers = TextAreaField(_l('Correct Answers (one per line for free-text)'), validators=[Optional()])
    points = IntegerField(_l('Points'), default=10, validators=[DataRequired()])
    requires_review = BooleanField(_l('Requires Manual Review (for free-text)'), default=False)
    submit = SubmitField(_l('Save Question'))

class EventForm(FlaskForm):
    name = StringField(_l('Event Name'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'))
    start_time = DateTimeLocalField(_l('Start Time'), format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField(_l('End Time'), format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    quiz_id = SelectField(_l('Quiz'), coerce=int, validators=[DataRequired()])
    submit = SubmitField(_l('Create Event'))

class TeamForm(FlaskForm):
    name = StringField(_l('Team Name'), validators=[DataRequired()])
    max_size = IntegerField(_l('Max Team Size'), default=5, validators=[DataRequired()])
    event_id = SelectField(_l('Event'), coerce=int, validators=[DataRequired()])
    submit = SubmitField(_l('Create Team'))
