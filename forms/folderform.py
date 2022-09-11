from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Regexp, InputRequired


class FolderForm(Form):
    title = StringField("Title", validators=[InputRequired()])
    description = TextAreaField("Title", validators=[InputRequired()])
