from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'C:/QA/generatedPython'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def edit_file(filename, title):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if request.method == 'POST':
        content = request.form['content']
        # Remove any extra newline characters at the end of each line
        content = '\n'.join([line.rstrip('\n') for line in content.splitlines()])
        with open(file_path, 'w') as file:
            file.write(content)
        # Redirect to the index page after saving changes
        return redirect(url_for('index'))

    with open(file_path, 'r') as file:
        content = file.read()

    return render_template('edit.html', content=content, title=title)

if __name__ == '__main__':
    app.run(debug=True)
