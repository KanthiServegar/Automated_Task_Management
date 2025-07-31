
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app.models import User, Task

main_bp = Blueprint('main_bp', __name__)



# User registration with role
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'developer')  # Default role

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('main_bp.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main_bp.login'))

    return render_template('register.html')


# User login
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main_bp.dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


# User logout
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main_bp.login'))

# Dashboard for logged-in user
# @main_bp.route('/dashboard')
# @login_required
# def dashboard():
#     tasks = Task.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', tasks=tasks)



# Dashboard for logged-in user
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Update overdue tasks before displaying tasks
    update_overdue_tasks()  # This will mark overdue tasks

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks)



# Create a task
@main_bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        importance = request.form['importance']
        progress = request.form.get('progress', '')

        new_task = Task(
            name=name,
            description=description,
            due_date=due_date,
            importance=importance,
            progress=progress,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('main_bp.dashboard'))

    return render_template('create_task.html')

# Edit a task
@main_bp.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('You are not authorized to edit this task.', 'danger')
        return redirect(url_for('main_bp.dashboard'))

    if request.method == 'POST':
        task.name = request.form['name']
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task.importance = request.form['importance']
        task.progress = request.form.get('progress', task.progress)
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('main_bp.dashboard'))

    return render_template('edit_task.html', task=task)



# Delete task
@main_bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Ensure that the user is authorized to delete the task
    if task.user_id != current_user.id:
        flash('You are not authorized to delete this task.', 'danger')
        return redirect(url_for('main_bp.dashboard'))

    # Delete the task from the database
    db.session.delete(task)
    db.session.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main_bp.dashboard'))

# Function to update overdue tasks
from datetime import datetime


def update_overdue_tasks():
    tasks = Task.query.filter(Task.status != 'Completed').all()
    for task in tasks:
        # Convert task.due_date to a datetime object, if it's a date object
        if isinstance(task.due_date, datetime):
            due_date = task.due_date
        else:
            # Convert task.due_date (which might be a date) to a datetime object
            due_date = datetime.combine(task.due_date, datetime.min.time())

        # Check if the task is overdue
        if due_date < datetime.now() and task.status != 'Overdue':
            task.status = 'Overdue'
            db.session.commit()

