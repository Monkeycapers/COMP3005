import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def main(name="Home"):
    return render_template("home.j2", name=name)

@app.route('/about')
def about(name="About"):
    return render_template("about.j2", name=name)