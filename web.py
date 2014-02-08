import os
import random

from flask import Flask, redirect, render_template, request
from pymongo import MongoClient

PER_PAGE = 10


# load doc ids

with open('docids.csv') as infile:
    doc_ids = sorted(set(int(l.strip()) for l in infile))

def random_id():
    return random.choice([id for id in doc_ids if id > 28000])


# the Flask app

client = MongoClient(os.environ.get('MONGOHQ_URL'))
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def thedata():
    page = int(request.args.get('page', 1))
    context = {
        'docs': client['app22023129'].registrations.find({}).limit(PER_PAGE),
    }
    return render_template('thedata.html', **context)

@app.route('/random')
def random_doc():
    return redirect('/%i' % random_id())

@app.route('/<int:doc_id>', methods=['GET', 'POST'])
def doc(doc_id):
    if request.method == 'POST':
        client['app22023129'].registrations.insert(dict(request.form.items()))
        return redirect('/%i' % random_id())
    context = {'doc_id': doc_id}
    return render_template('doc.html', **context)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
