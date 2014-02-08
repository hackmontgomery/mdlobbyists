import os
import random

from flask import Flask, redirect, render_template, request
from pymongo import MongoClient

PER_PAGE = 100


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

    filtered = False

    spec = {}

    valid_filters = ['lobbyist_name', 'firm_name', 'employer_name']
    for key in valid_filters:
        if key in request.args:
            spec[key] = request.args[key]

    qs = client['app22023129'].registrations.find(spec)

    context = {
        'total_count': qs.count(),
        'docs': qs.sort('doc_id').limit(PER_PAGE),
        'filtered': bool(spec),
    }
    return render_template('thedata.html', **context)

@app.route('/data/<doc_id>')
def a_doc(doc_id):
    doc = client['app22023129'].registrations.find_one({'doc_id': doc_id})
    context = {'doc': doc}
    return render_template('doc.html', **context)

@app.route('/random')
def random_doc():
    return redirect('/%i' % random_id())

@app.route('/<doc_id>', methods=['GET', 'POST'])
def doc(doc_id):
    if request.method == 'POST':
        client['app22023129'].registrations.insert(dict(request.form.items()))
        return redirect('/%i' % random_id())
    context = {'doc_id': doc_id}
    return render_template('doc_form.html', **context)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
