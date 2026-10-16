from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_babel import lazy_gettext as _l

class TeamCreateForm(FlaskForm):
    name = StringField(_l('Team Name'), validators=[DataRequired(), Length(min=2, max=64)])
    max_size = IntegerField(_l('Max Team Size'), default=5, validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField(_l('Register Team'))
