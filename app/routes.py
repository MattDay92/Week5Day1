from app import app
# from folder called app - import the variable app from __init__.py

from flask import render_template, request, redirect, url_for, flash
from .forms import UserCreationForm, LoginForm, PostForm, SearchForm
from .models import User, Post, Likes
from flask_login import login_user, logout_user, current_user, login_required
import requests
import os
from werkzeug.security import check_password_hash

NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

@app.route('/index')
@app.route('/')
def homePage():
    people = ['Shoha', 'Brandt', 'Aubrey']
    text = 'SENDING THIS FROM PYTHON!'
    return render_template('index.html', people = people, my_text = text)
                                        #keyword = value
    ### You provide the name of the file index.html (or whatever you want to call it)
    ### The HTML doesn't have to be static anymore!


@app.route('/contact')
def contact():
    users = User.query.all()
    if current_user.is_authenticated:
        who_i_am_following = {u.id for u in current_user.followed.all()}
        for user in users:
            if user.id in who_i_am_following:
                user.following = True

    return render_template('contact.html', users = users)

@app.route('/signup', methods=['GET', 'POST'])
def signUpPage():
    form = UserCreationForm()
    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            print(username, email, password)

            # add user to database
            user = User(username, email, password)
            
            user.saveToDB()

            return redirect(url_for('contact'))
            # provide the name of the FUNCTION we're redirecting to


    return render_template('signup.html', form = form)


@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    form = LoginForm()
    # must import this form at the top of the page

    if request.method == "POST":
        # Only get a POST method when a form is being submitted
        if form.validate():
            username = form.username.data
                    #go to the form, get the username data that was submitted
            password = form.password.data

            # check if user with that username even exists
            # the first() gets back the first response in the db - but usernames are unique so it doesn't matter
            user = User.query.filter_by(username=username).first()
            # .query comes from SQLAlchemy - db.Model - DOCUMENTATION
            if user: 
                # if user exists - check if passwords match
                if check_password_hash(user.password, password):
                    login_user(user)
                    flash(f"Successfully logged in!  Welcome back {user.username}", category='success')
                    return redirect(url_for('getPost'))
                else:
                    flash('WRONG PASSWORD', category='danger')
            else:
                flash('User doesn\'t exist', category='danger')


    return render_template('login.html', form = form)
    #                                   HTML  ROUTE

    
@app.route('/logout', methods=["GET"])
@login_required
def logoutRoute():
    logout_user()

    return redirect(url_for('loginPage'))

@app.route('/posts/create', methods=["GET", "POST"])
@login_required
def createPost():
    form = PostForm()
# Have to import the Post Form at the top from forms.py
    if request.method == "POST":
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data

        post = Post(title, img_url, caption, current_user.id)
        post.saveToDB()

    return render_template('createpost.html', form = form)

@app.route('/posts', methods=["GET"])
def getPost():
    posts = Post.query.all()
    # Finding likes based on User
    if current_user.is_authenticated:
        my_likes = Likes.query.filter_by(user_id=current_user.id).all()
        my_likes_set = set()
        for like in my_likes:
            my_likes_set.add(like.post_id)
        likes = {like.post_id for like in my_likes} ###set comprehension

        for p in posts:
            if p.id in likes:
                p.liked = True

    # Find likes based on Post
    # for post in posts:
    #     post.like_counter = len(Likes.query.filter_by(post_id=post.id).all())
    # Instead of this for loop... use post.getLikeCount that we made in models


    return render_template('feed.html', posts = posts)

# DYNAMIC ROUTING
@app.route('/posts/<int:post_id>', methods=['GET'])
def singlePost(post_id):
    post = Post.query.get(post_id)
    return render_template('singlepost.html', post=post)

@app.route('/posts/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def updatePost(post_id):
    post = Post.query.get(post_id)
    if current_user.id != post.author.id:
        return redirect(url_for('getPosts'))
    form = PostForm()
    if request.method == 'POST':
        if form.validate():
            title = form.title.data
            img_url = form.img_url.data
            caption = form.caption.data
            post.title = title
            post.img_url = img_url
            post.caption = caption

            post.saveChanges()

            return redirect(url_for('getPost', post_id = post.id))

    return render_template('updatepost.html', post=post, form=form)


@app.route('/posts/<int:post_id>/delete', methods=["GET"])
@login_required
def deletePost():
    post = Post.query.all()
    if current_user.id != post.author.id:
        return redirect(url_for('getPosts'))
    
    post.deleteFromDB()

    return redirect(url_for('getPosts'), post = post)


@app.route('/posts/<int:post_id>/like', methods=["GET", "POST"])
@login_required
def likePost(post_id):
    like_instance = Likes(current_user.id, post_id)
    like_instance.saveToDB()

    return redirect(url_for('getPost'))

@app.route('/posts/<int:post_id>/unlike', methods=["GET", "POST"])
@login_required
def unlikePost(post_id):
    like_instance = Likes.query.filter_by(post_id = post_id).filter_by(user_id = current_user.id).first()
    like_instance.deleteFromDB()

    return redirect(url_for('getPost'))


@app.route('/follow/<int:user_id>', methods=["GET", "POST"])
@login_required
def followUser(user_id):
    person = User.query.get(user_id)
    current_user.follow(person)

    return redirect(url_for('contact'))

@app.route('/unfollow/<int:user_id>', methods=["GET", "POST"])
@login_required
def unfollowUser(user_id):
    person = User.query.get(user_id)
    current_user.unfollow(person)

    return redirect(url_for('contact'))

@app.route('/news', methods = ["GET", "POST"])
def newsPage():

    my_form = SearchForm()
    if request.method == "POST":
        if my_form.validate():
            search_term = my_form.search.data
            url = f"https://newsapi.org/v2/everything?q={search_term}&apiKey={NEWS_API_KEY}&pagesize=20"
                                                                                #Can add my own page size

            result = requests.get(url)

            if result.ok:
                data = result.json()
                articles = data['articles']
                return render_template('news.html', html_form = my_form, articles = articles)


    return render_template('news.html', html_form = my_form)



