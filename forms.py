from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    name = StringField("Nazwa", validators=[DataRequired()])
    submit = SubmitField("Zarejestruj mnie!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zaloguj mnie!")

class TaskForm(FlaskForm):
    task = StringField("Dodaj nowe zadanie", validators=[DataRequired()])
    submit = SubmitField("Dodaj zadanie!")