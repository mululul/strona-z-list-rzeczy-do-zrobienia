from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from forms import RegisterForm, LoginForm, TaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

# Initialize SQLAlchemy outside the if __name__ == "__main__": block
db = SQLAlchemy(app)  # Use the same app instance here
Bootstrap5(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    tasks = relationship("Task", back_populates="user")

class Task(db.Model):
    __tablename__ = "tasks"
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")


def only_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated:
            return render_template("need_to_login.html")
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home_page.html", current_user=current_user)

@app.route('/zarejestruj', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("Jesteś już zarejestrowany na ten email, zaloguj się!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)

@app.route('/zaloguj', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("Ten email nie znajduje się wśród naszych użytkowników. Spróbuj ponownie.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Hasło nieprawidłowe, spróbuj ponownie.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)

@app.route('/wyloguj')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/moja-lista', methods=["GET", "POST"])
@only_logged_in
def tasks():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            task=form.task.data,
            user=current_user
        )
        db.session.add(new_task)
        db.session.commit()
    user_tasks = current_user.tasks
    return render_template('tasks.html', tasks=user_tasks, form=form)


@app.route("/zadanie-gotowe/<int:task_id>", methods=["GET", "POST"])
def task_done(task_id):
    task_to_be_done = Task.query.get_or_404(task_id)
    db.session.delete(task_to_be_done)
    db.session.commit()
    return redirect(url_for('tasks'))
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)