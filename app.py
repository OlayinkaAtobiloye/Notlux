#!usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import TextAreaField, SelectField

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
app.SQLALCHEMY_TRACK_MODIFICATIONS = False
app.debug = True


# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/notlux'

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)

from models.folder import Folder
from models.note import Note
from forms.noteform import NoteForm
from forms.folderform import FolderForm

'''If everything works fine you will get a
message that Flask is working on the first
page of the application
'''


@app.route("/")
def index():
    folders = list(Folder.query.all())
    notes = Note.query.all()
    uncategorized_notes = list(Note.query.filter(Note.folder_id == None))
    if len(uncategorized_notes) >= 1:
        uncategorized = Folder(title="Uncategorized", description="All uncategorized notes go here.", id=0)
        folders.insert(0, uncategorized)
    return render_template("index.html", notes=notes, folders=folders)


@app.route("/notes/create", methods=["GET"])
def create_note_template():
    form = NoteForm()
    return render_template("forms/new_note.html", form=form)


@app.route("/notes", methods=["POST"])
def create_note():
    form = NoteForm(request.form)
    if form.validate():
        try:
            note = Note(title=request.form.get("title"),
                        description=request.form.get("description"),
                        folder_id=request.form.get("folder_id"))
            db.session.add(note)
            db.session.commit()
            return redirect(url_for("display_notes"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Note ' + request.form['title'] + f' could not be created! {e}')
            return redirect(url_for("display_notes"))
    else:
        flash(f'An error occurred, Please check form and try again')
        return redirect(url_for("index"))


@app.route("/notes", methods=["GET"])
def display_notes():
    notes = Note.query.all()
    return render_template("notes.html", notes=notes)


@app.route("/notes/<int:note_id>", methods=["GET"])
def display_note_using_id(note_id):
    note = Note.query.get(note_id)
    return render_template("pages/show-note.html", note=note)


@app.route("/notes/<int:note_id>/edit", methods=["GET"])
def create_edit_note_template(note_id):
    note = Note.query.get(note_id)
    form = NoteForm
    setattr(form, "description", TextAreaField(default=note.description))
    form = NoteForm()
    return render_template("forms/edit-note.html", note=note, form=form)


@app.route("/notes/<int:note_id>/edit", methods=["POST"])
def edit_note(note_id):
    form = NoteForm(request.form)
    if form.validate():
        note = Note.query.get(note_id)
        try:
            note.title = request.form.get("title")
            note.description = request.form.get("description")
            note.folder_id = request.form.get("folder")
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Note ' + request.form['title'] + f' could not be updated! {e}')
            return redirect(url_for(f"index"))
    else:
        flash('An error occurred. Please check form and try again.')
    return redirect(url_for(f"display_note_using_id", note_id=note_id))


@app.route("/notes/<int:note_id>/delete", methods=["DELETE", "POST"])
def delete_note(note_id):
    note = Note.query.get(note_id)
    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Folder ' + request.form['title'] + f' could not be deleted! {e}')
    return redirect(url_for(f"index"))


@app.route("/folders", methods=["GET"])
def display_folders():
    folders = list(Folder.query.all())
    uncategorized_notes = list(Note.query.filter(Note.folder_id == None))
    if len(uncategorized_notes) >= 1:
        uncategorized = Folder(title="Uncategorized", description="All uncategorized notes go here.", id=0)
        folders.insert(0, uncategorized)
    return render_template("folders.html", folders=folders)


@app.route("/folders", methods=["POST"])
def create_folder():
    form = FolderForm(request.form)
    if form.validate():
        try:
            folder = Folder(title=request.form.get("title"),
                            description=request.form.get("description"))
            db.session.add(folder)
            db.session.commit()
            return redirect(url_for("display_folders"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Folder ' + request.form['title'] + f' could not be created! {e}')
            return redirect(url_for("index"))
    else:
        flash(f'An error occurred. Please check form and try again')
    return redirect(url_for("index"))


@app.route("/folders/create", methods=["GET"])
def create_folder_template():
    form = FolderForm(request.form)
    return render_template("forms/new_folder.html", form=form)


@app.route("/folders/<int:folder_id>", methods=["GET"])
def display_folder_using_id(folder_id):
    if folder_id == 0:
        uncategorized_notes = list(Note.query.filter(Note.folder == None))
        folder = Folder(title="Uncategorized", description="All uncategorized notes go here.", id=0,
                        notes=uncategorized_notes)
    else:
        folder = Folder.query.get(folder_id)
    return render_template("pages/show-folder.html", folder=folder)


@app.route("/folders/<int:folder_id>/edit", methods=["GET"])
def create_edit_folder_template(folder_id):
    form = FolderForm(request.form)
    folder = Folder.query.get(folder_id)
    return render_template("forms/edit-folder.html", folder=folder, form=form)


@app.route("/folders/<int:folder_id>/edit", methods=["POST"])
def edit_folder(folder_id):
    folder = Folder.query.get(folder_id)
    form = FolderForm(request.form)
    if form.validate():
        try:
            folder.title = request.form.get("title")
            folder.description = request.form.get("description")
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Folder ' + request.form['title'] + f' could not be updated! {e}')
    else:
        flash(f'An error occurred, Please check form and try again')
    return redirect(url_for(f"display_folder_using_id", folder_id=folder_id))


@app.route("/folders/<int:folder_id>/delete", methods=["DELETE", "POST"])
def delete_folder(folder_id):
    folder = Folder.query.get(folder_id)
    try:
        db.session.delete(folder)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Folder ' + request.form['title'] + f' could not be deleted! {e}')
    return redirect(url_for(f"index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run()
