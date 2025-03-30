from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

@app.route('/')
def index():
    filter_val = request.args.get('filter', 'all')
    if filter_val == 'active':
        todo_list = Todo.query.filter_by(complete=False).all()
    elif filter_val == 'complete':
        todo_list = Todo.query.filter_by(complete=True).all()
    else:
        todo_list = Todo.query.all()

    return render_template('login.html', todo_list=todo_list, filter_val=filter_val)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Account.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)


@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    filter_val = request.args.get("filter", "all")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index", filter=filter_val))

@app.route('/edit', methods=["POST"])
def edit():
    todo_id = request.form.get("todo_id")
    new_title = request.form.get("title")
    filter_val = request.form.get("filter", "all")
    todo = Todo.query.get(todo_id)
    todo.title = new_title
    db.session.commit()
    return redirect(url_for("index", filter=filter_val))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    filter_val = request.args.get("filter", "all")
    todo = Todo.query.get(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index", filter=filter_val))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    filter_val = request.args.get("filter", "all")
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index", filter=filter_val))



if __name__ == '__main__':
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()

    app.run(debug=True)
