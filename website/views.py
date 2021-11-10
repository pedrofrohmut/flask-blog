from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user

from . import db
from .models import Post, User, Comment, Like

views = Blueprint("views", __name__)


def add_likeds(post):
    liked = any(like.post_id == post.id and like.user_id == current_user.id for like in post.likes)
    post.liked = liked
    return post


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    posts_with_likeds = map(add_likeds, posts)
    return render_template("home.html", user=current_user, posts=posts_with_likeds)


@views.route("/posts/add", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        content = request.form.get("text") or ""
        if content == "":
            flash("Content is required and cannot be empty", category="error")
            return redirect(url_for("views.add_post"))
        post = Post(content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post created", category="success")
        return redirect(url_for("views.add_post"))
    return render_template("add_post.html", user=current_user)


@views.route("/posts/delete/<post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        flash("Post does not exist", category="error")
    if post.user_id != current_user.id:
        flash("User is not the post owner. Permission denied", category="error")
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted", category="success")
    return redirect(url_for("views.home"))


@views.route("/posts/<username>")
@login_required
def list_posts_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User doesn't exists", category="error")
        return redirect(url_for("views.home"))
    return render_template("posts.html", user=current_user, url_username=username, posts=user.posts)


@views.route("/comments", methods=["POST"])
@login_required
def add_comment():
    content = request.form.get("commentText") or ""
    post_id = request.form.get("postId") or ""
    if content == "":
        flash("Comment cannot be empty", category="error")
        return redirect(url_for("views.home"))
    if post_id == "":
        flash("Post id not informed", category="error")
        return redirect(url_for("views.home"))
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        flash("Post doesn't exists", category="error")
        return redirect(url_for("views.home"))
    comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    flash("Comment added", category="success")
    return redirect(url_for("views.home"))


@views.route("/comments/delete/<comment_id>")
@login_required
def delete_comment(comment_id):
    if comment_id == "":
        flash("Comment id not informed", category="error")
        return redirect(url_for("views.home"))
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        flash("Comment doesn't exists", category="error")
        return redirect(url_for("view.home"))
    if comment.user_id != current_user.id:
        flash("User is not the comment owner. Permission denied", category="error")
        return redirect(url_for("views.home"))
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted", category="success")
    return redirect(url_for("views.home"))


@views.route("/likes/toggle", methods=["POST"])
@login_required
def toggle_like():
    post_id = request.form.get("postId") or ""
    user_id = request.form.get("userId") or ""
    if post_id == "":
        flash("Post id not informed", category="error")
        return redirect(url_for("views.home"))
    if user_id == "":
        flash("User id not informed", category="error")
        return redirect(url_for("views.home"))
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        flash("Post does not exist", category="error")
        return redirect(url_for("views.home"))
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash("User does not exists", category="error")
        return redirect(url_for("views.home"))
    old_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if old_like:
        db.session.delete(old_like)
        db.session.commit()
        flash("Like removed", category="success")
        return redirect(url_for("views.home"))
    else:
        like = Like(post_id=post_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
        flash("Like added", category="success")
        return redirect(url_for("views.home"))
