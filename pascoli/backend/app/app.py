from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
import datetime


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Não autorizado!"})

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
        except:
            return jsonify({"message": "Token inválido!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


app = Flask(__name__)

app.config["SECRET_KEY"] = "postgres"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@db:5432/postgres"

db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(32), nullable=False)


with app.app_context():
    db.create_all()
    db.session.add(User(email="teste@teste.com", password="teste"))
    db.session.commit()


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/notes")
def todos():
    todos = Todo.query.all()
    return render_template("notes.html", todos=todos)


# Restante do código (rotas de login, logout, adição de tarefas) permanece o mesmo


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    new_user = User(email=data["email"], password=data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User {new_user.email} created successfully!"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"], password=data["password"]).first()

    if user:
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"token": token})
    else:
        return jsonify({"message": "Dados inválidos"}), 401


@app.route("/add/todo", methods=["POST"])
@token_required
def add_todo(current_user):
    data = request.get_json()
    new_todo = Todo(text=data["text"])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"message": f"Todo created successfully!"})


@app.route("/delete/todo", methods=["POST"])
@token_required
def delete_todo(current_user):
    data = request.get_json()
    deletable_todo = Todo.query.filter_by(id=data["id"]).first()
    db.session.delete(deletable_todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted successfully!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
