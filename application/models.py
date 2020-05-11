from application import db, ma
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(30), unique=True)
    password = Column(String(30))
    first_name = Column(String(30))
    last_name = Column(String(30))

    tutorials = relationship('Tutorial', secondary='user_tutorials', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<user %r>' % self.first_name


class Tutorial(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    price = Column(Integer)
    description = Column(String(200))

    def __repr__(self):
        return '<Tutorial %r>' % self.name


db.Table('user_tutorials',
         Column('user_id', Integer, ForeignKey('user.id')),
         Column('tutorial_id', Integer, ForeignKey('tutorial.id')))


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password', 'first_name', 'last_name')


class TutorialSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'price', 'description')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
tutorial_schema = TutorialSchema()
tutorials_schema = TutorialSchema(many=True)
