from app import db


class Folder(db.Model):
    __tablename__ = "folders"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(20), nullable=False)
    notes = db.relationship('Note', backref="folder", lazy=True)

    def __repr__(self):
        return f"Folder - {self.title}"
