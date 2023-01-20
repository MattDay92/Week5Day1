from app import app
# from folder called app - import the variable app from __init__.py

from flask import render_template, request, redirect, url_for
from .forms import UserCreationForm
from .models import User

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
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

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
