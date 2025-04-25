from .plugin import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
    

class Drug(db.Model):
    __tablename__ = 'drug'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    drug_id = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)


class Relation(db.Model):
    __tablename__ = 'relation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_id_1 = db.Column(db.String(20), nullable=False)
    drug_id_2 = db.Column(db.String(20), nullable=False)
    relation = db.Column(db.Integer, nullable=False)
