from app import app

# This if statements means that this is the start of the file and stops the server from accidentily running
# Makes sure that anything under the if statement is being ran as a SCRIPT

if __name__ == '__main__':
    app.run()