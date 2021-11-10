from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email") or ""
        password = request.form.get("password") or ""

        if len(email) < 5:
            flash("E-mail must be at least 5 characters", category="error")
            return redirect(url_for("auth.sign_in"))

        if len(password) < 3:
            flash("Password must be at least 3 characters", category="error")
            return redirect(url_for("auth.sign_in"))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash(
                "User not found with this e-mail. Please recheck yout e-mail or go to register",
                category="error"
            )
            return redirect(url_for("auth.sign_in"))

        password_match = check_password_hash(user.password_hash, password)
        if not password_match:
            flash(
                "Password not correct or does not match this e-mail. Please recheck your password",
                category="error")
            return redirect(url_for("auth.sign_in"))

        login_user(user, remember=True)
        flash("User logged in", category="success")
        return redirect(url_for("views.home"))

    return render_template("sign_in.html", user=current_user)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username") or ""
        email = request.form.get("email") or ""
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirmPassword") or ""

        print("SIGN UP CALLED!")
        print(username, email, password)

        if len(username) < 3:
            flash("Username must be at least 3 characters", category="error")
            return redirect(url_for("auth.sign_up"))

        if len(email) < 5:
            flash("E-mail must be at least 5 characters", category="error")
            return redirect(url_for("auth.sign_up"))

        if len(password) < 3:
            flash("Password must be at least 3 characters", category="error")
            return redirect(url_for("auth.sign_up"))

        if password != confirm_password:
            flash("Confirm password doesn't match the password", category="error")
            return redirect(url_for("auth.sign_up"))

        registered_user_by_email = User.query.filter_by(email=email).first()
        if registered_user_by_email:
            flash("E-mail is already taken", category="error")
            return redirect(url_for("auth.sign_up"))

        registered_user_by_username = User.query.filter_by(username=username).first()
        if registered_user_by_username:
            flash("Username already taken", category="error")
            return redirect(url_for("auth.sign_up"))

        hashed_password = generate_password_hash(password, method="sha256")
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("User created", category="success")
        return redirect(url_for("auth.sign_in"))

    return render_template("sign_up.html", user=current_user)


@auth.route("/sign-out")
@login_required
def sign_out():
    logout_user()
    return redirect(url_for("auth.sign_in"))
