import os
import random
from flask import Flask, redirect, render_template, request


# load doc ids

with open('docids.csv') as infile:
    doc_ids = sorted(set(int(l.strip()) for l in infile))

def random_id():
    return random.choice([id for id in doc_ids if id > 28000])


# the Flask app

app = Flask(__name__)

@app.route('/')
def index():
    # return render_template('index.html')
    return redirect('/%i' % random_id())

@app.route('/random')
def random_doc():
    return redirect('/%i' % random_id())

@app.route('/<int:doc_id>', methods=['GET', 'POST'])
def doc(doc_id):
    if request.method == 'POST':
        print request.form
        return redirect('/%i' % random_id())
    context = {'doc_id': doc_id}
    return render_template('doc.html', **context)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
