from werkzeug import check_password_hash, generate_password_hash
from flask import Flask , g, url_for, redirect,flash, render_template, session, _app_ctx_stack,request

from datetime import datetime

from B2C import db, app
#models
from models import User, Comment, Item, Address, Order

#docra login_required
from functools import wraps

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(id = session['user_id']).first()


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_user_id(email = None):
    return User.query.filter_by(email = email).first()

@app.route("/")
def index():
    return render_template("web/home.html")

@login_required
@app.route("/add_adress")
def add_address():
    pass

@login_required
@app.route("/edit_address")
def edit_address():
    pass

@login_required
@app.route("/delete_address")
def delete_address():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email = request.form['email']).first()
        if user is None:
            error = 'Invalid email address'
        elif not check_password_hash(user.pw_hash,
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('web/login.html', error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif get_user_id(request.form['email']) is not None:
            error = 'The email is already taken'
        else:
            user = User(request.form['username'], request.form['email'], generate_password_hash(request.form['password']))
            db.session.add(user)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('web/register.html', error=error)

@login_required
@app.route("/edit_profile")
def edit_profie():
    pass

