from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import signal
import sys

app = Flask(__name__)
UPLOAD_FOLDER = 'C:/QA/generatedPython'   # Make sure this points to your .git directory
ALLOWED_EXTENSIONS = {'.txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flag to indicate if the application should stop
stop_event = False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file1', methods=['GET', 'POST'])
def edit_file1():
    return edit_file('configExample.txt', 'Edit configExample.txt')

@app.route('/file2', methods=['GET', 'POST'])
def edit_file2():
    return edit_file('configExample2.txt', 'Edit configExample2.txt')

@app.route('/file3', methods=['GET', 'POST'])
def edit_file3():
    return edit_file('configExample3.txt', 'Edit configExample3.txt')

@app.route('/stop', methods=['POST'])
def stop_server():
    global stop_event
    stop_event = True
    # Get the process ID of the Flask server
    pid = os.getpid()
    # Send a SIGTERM signal to the Flask server process
    os.kill(pid, signal.SIGTERM)
    return "Server is stopping..."

def edit_file(filename, title):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if request.method == 'POST':
        content = request.form['content']
        # Remove any extra newline characters at the end of each line
        content = '\n'.join([line.rstrip('\n') for line in content.splitlines()])
        with open(file_path, 'w') as file:
            file.write(content)

        # Commit and push changes to the repository
        commit_message = 'Updated {}'.format(filename)
        subprocess.run(['git', 'add', file_path], cwd=app.config['UPLOAD_FOLDER'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=app.config['UPLOAD_FOLDER'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=app.config['UPLOAD_FOLDER'], check=True)

        # Redirect to the index page after saving changes
        return redirect(url_for('index'))

    with open(file_path, 'r') as file:
        content = file.read()

    return render_template('edit.html', content=content, title=title)

def signal_handler(sig, frame):
    global stop_event
    print('You pressed Ctrl+C!')
    stop_event = True
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    app.run(debug=True)

