import math
import os
import random
import urllib

from bson import json_util
from flask import Flask, Response, redirect, render_template, request
from pymongo import MongoClient

PER_PAGE = 20


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
    offset = (page - 1) * PER_PAGE

    filtered = False

    filters = {}

    valid_filters = ['lobbyist_name', 'firm_name', 'employer_name']
    for key in valid_filters:
        if key in request.args:
            filters[key] = request.args[key]

    print filters

    qs = client['app22023129'].registrations.find(filters)

    total_docs = qs.count()
    total_pages = int(math.ceil(total_docs / float(PER_PAGE)))

    context = {
        'total_count': total_docs,
        'total_pages': total_pages,
        'page': page,
        'next_page': page + 1 if page < total_pages else None,
        'previous_page': page - 1 if page > 1 else None,
        'docs': qs.sort('doc_id').limit(PER_PAGE).skip(offset),
        'filter_qs': urllib.urlencode(filters),
        'filtered': bool(filters),
    }
    return render_template('thedata.html', **context)

@app.route('/data/<doc_id>')
def a_doc(doc_id):
    doc = client['app22023129'].registrations.find_one({'doc_id': doc_id})
    context = {'doc': doc}
    return render_template('doc.html', **context)

@app.route('/data/<doc_id>.json')
def a_doc_api(doc_id):
    doc = client['app22023129'].registrations.find_one({'doc_id': doc_id})
    return Response(json_util.dumps(doc), mimetype='application/json')

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
