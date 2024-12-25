from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Set up the database (using SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Task and Diary classes (these represent the database tables)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)  # Ensure this column is defined


class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Define Movie Watchlist class
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    watched = db.Column(db.Boolean, default=False)  # Track if the movie has been watched

# Home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reset-db')
def reset_db():
    # WARNING: This will delete all data in the database!
    db.drop_all()
    db.create_all()
    return "Database has been reset!"

# Login page for user selection (Siri or Nani)
@app.route('/login', methods=['POST'])
def login():
    user = request.form['user']
    password = request.form['password']
    
    # Check if the passwords match
    if (user == 'Siri' and password == 'Nani') or (user == 'Nani' and password == 'Siri'):
        return redirect(url_for('main_page', user=user))
    else:
        return "Incorrect password, please try again."

# Main page after login (Go to To-Do List or Diary)
@app.route('/main/<user>')
def main_page(user):
    return render_template('main.html', user=user)

# To-Do List page
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        task_desc = request.form['description']
        task = Task(description=task_desc)
        db.session.add(task)
        db.session.commit()
    tasks = Task.query.all()
    return render_template('todo.html', tasks=tasks)

# Mark task as completed
@app.route('/todo/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('todo'))

# Delete a task
@app.route('/todo/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('todo'))

# Diary Entry page
@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        entry = Diary(name=name, content=content)
        db.session.add(entry)
        db.session.commit()
    entries = Diary.query.all()
    return render_template('diary.html', entries=entries)

# Movie Watchlist page
@app.route('/watchlist', methods=['GET', 'POST'])
def watchlist():
    if request.method == 'POST':
        movie_title = request.form['title']
        movie = Movie(title=movie_title)
        db.session.add(movie)
        db.session.commit()
    movies = Movie.query.all()
    return render_template('watchlist.html', movies=movies)

# Mark movie as watched
@app.route('/watchlist/watched/<int:movie_id>')
def watched_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie.watched = True
    db.session.commit()
    return redirect(url_for('watchlist'))

# Delete a movie from the watchlist
@app.route('/watchlist/delete/<int:movie_id>')
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('watchlist'))

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('home'))  # Redirect to the home (login) page


# Add app context for db creation
if __name__ == '__main__':
    with app.app_context():  # This ensures the app context is available
        db.create_all()  # Creates the database tables if they don't exist
    app.run(debug=True)
