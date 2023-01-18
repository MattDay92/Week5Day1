from app import app
# from folder called app - import the variable app from __init__.py

from flask import render_template

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
