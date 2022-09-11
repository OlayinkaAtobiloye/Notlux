from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Regexp, InputRequired, DataRequired

from models.folder import Folder

folders = Folder.query.all()
folders = list(map(lambda folder: (folder.id, folder.title), folders))
folders.insert(0, ("", ""))


class NoteForm(Form):
    title = StringField("Title", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    folder_id = SelectField("Folder", choices=folders)
