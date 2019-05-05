from . import app
from flask import render_template

@app.route('/')
@app.route('/results')
def index():
    return render_template("index.html")

