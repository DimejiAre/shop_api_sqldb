import uuid
from models.shared import db
from werkzeug.security import generate_password_hash


class User(db.Model):
    __name__ = 'user'
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Integer, nullable=False)
    id = db.Column(db.VARCHAR, primary_key=True, nullable=False)
    items = db.relationship('Item', cascade='all,delete', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def create(username, password, admin=0, id=None):
        if id is None:
            id = uuid.uuid4().hex
        else:
            id = id
        user = User(username=username, password=generate_password_hash(password, 'sha1'), admin=admin, id=id)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def json_data(username, password, admin, id):
        return {
            "username": username,
            "password": password,
            "admin": admin,
            "id": id
        }

    @staticmethod
    def view():
        user_list = []
        for user in User.query.all():
            user_list.append(User.json_data(user.username, user.password, user.admin, user.id))
        return user_list

    @staticmethod
    def find_one(id):
        user = User.query.filter_by(id=id).first()
        if user:
            return User.json_data(user.username, user.password, user.admin, user.id)
        else:
            return None

    @staticmethod
    def find_by_username(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return User.json_data(user.username, user.password, user.admin, user.id)
        else:
            return None

    @staticmethod
    def find_userclass_by_username(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return user
        else:
            return None

    @staticmethod
    def update(id, username=None, password=None, admin=None):
        user = User.query.filter_by(id=id).first()
        if username is not None:
            user.username = username
        if password is not None:
            user.password = generate_password_hash(password, 'sha1')
        if admin is not None:
            user.admin = admin
        db.session.commit()

    @staticmethod
    def delete(id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()







