from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, UserLogin, FeedbackForm
from sqlalchemy.exc import IntegrityError
import os
import re


app = Flask(__name__)
app.app_context().push()


uri = os.environ.get('DATABASE_URL', 'postgresql:///feedbacks')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","helloworld1")
print(app.config["SECRET_KEY"])
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def home_page():
    return redirect ('/register')

@app.route('/register',methods=["GET","POST"])
def register_user():
    if "username" in session:
        return redirect (f"/users/{session['username']}")

    form=UserForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        new_user= User.register(username,password,email,first_name,last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)

        session["username"]=new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template("register.html",form=form)

@app.route('/login',methods=["GET","POST"])
def login():
    if "username" in session:
        return redirect (f"/users/{session['username']}")
        
    form= UserLogin()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.first_name}!", "primary")
            session["username"] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template("login.html",form=form)

@app.route("/users/<username>")
def secret(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    user=User.query.get_or_404(username)
    if user.username == session["username"]:
        return render_template('user_info.html',user=user)
    else:
        flash("Bad request", 'danger')
        return redirect (f"/users/{session['username']}")

@app.route("/users/<username>/feedback/add",methods=["GET","POST"])
def add_feedback(username):
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    form=FeedbackForm()
    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data
        new_feedback=Feedback(title=title,content=content,username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Successfully Added Your feedback!', "success")
        return redirect(f'/users/{username}')


    return render_template("feedback_form.html",form=form)

@app.route("/users/<username>/delete",methods=["POST"])
def delete_user(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    username=User.query.get_or_404(username)
    db.session.delete(username)
    session.pop("username")
    db.session.commit()
    flash("User Deleted", "danger")

    return redirect ('/register')

@app.route('/feedback/<int:id>/update',methods=["GET","POST"])
def edit_feedback(id):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    feedback = Feedback.query.get_or_404(id)

    if feedback.user.username != session["username"]:
        flash("Bad Request", "danger")
        return redirect (f'/users/{session["username"]}')

    form=FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data
        feedback.title=title
        feedback.content=content
        db.session.commit()
        flash('Successfully Edited!', "success")
        return redirect(f"/users/{feedback.user.username}")
    return render_template('feedback_form.html',form=form)


@app.route("/feedback/<int:id>/delete",methods=["POST"])
def delete_feedback(id):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    feedback = Feedback.query.get_or_404(id)
    if feedback.user.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash("feedback deleted", "info")
    return redirect(f"/users/{feedback.user.username}")


@app.route('/logout')
def logout_user():
    session.pop("username")
    flash("Goodbye!", "info")
    return redirect('/login')