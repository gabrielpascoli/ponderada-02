from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'  # Banco de dados SQLite

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)

db.create_all()

@app.route('/')
def index():
    if 'username' in session:
        todos = Todo.query.all()
        return render_template('notes.html', todos=todos)
    return redirect(url_for('login'))

# Restante do código (rotas de login, logout, adição de tarefas) permanece o mesmo

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
