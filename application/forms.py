from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, DateTimeField
from wtforms.validators import Email, DataRequired, Length, EqualTo, ValidationError
from application.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired("Entire Email"), Email()])
    password = PasswordField("Password", validators=[DataRequired("Entire password"), Length(min=3, max=15)])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=15)])
    confirm_password = PasswordField("Confirm password",validators=[DataRequired(), Length(min=6, max=15), EqualTo('password')])
    first_name = StringField("First name", validators=[DataRequired(), Length(min=3, max=30)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(min=3, max=30)])
    submit = SubmitField("Register now")

    def validate_email(self, email):
        result = User.query.filter(User.email == email.data).first()
        if result:
            raise ValidationError("Email already exist")


class AddTutorial(FlaskForm):
    name = StringField("Tutorial name", validators=[DataRequired(), Length(min=2, max=100)])
    price = IntegerField("Price", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10, max=100)])
    submit = SubmitField("Add tutorial")

    def validate_name(self, name):
        if len(name.data) < 2:
            raise ValidationError("Name is short")
        if len(name.data) > 100:
            raise ValidationError("Name is thoo long")
