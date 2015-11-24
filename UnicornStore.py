from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import json_util

app = Flask(__name__)
# app = Flask('UnicornStore')

#client = MongoClient(host='localhost', port=27017)
client = MongoClient('mongodb://unicornstore:unicornstore@ds049084.mongolab.com:49084/unicornstore')

database = client.get_database('unicornstore')
collection = database.get_collection('unicornstore')


@app.route("/")
def index():
    """Front Page"""
    return render_template('welcome.html')


@app.route("/nearby")
def getNearByItems():
    """Get 10 nearest items"""
    nearByItems = []
    location = [float(coordinate) for coordinate in request.args.get('location').split(',')]
    for document in collection.find({"location": {"$near": location}}).limit(10):
        nearByItems.append(document)

    return json_util.dumps(nearByItems)


@app.route("/deals")
def getBestDeals():
    """Get 3 best deals"""
    bestDeals = []
    deals = collection.aggregate([{
        '$project': {
            '_id': 0,
            'id': 1,
            'title': 1,
            'description': 1,
            'purchase_year': 1,
            'price': 1,
            'original_price': 1,
            'locality': 1,
            'pics': 1,
            'discount': {'$subtract': ['$price', '$original_price']}
        }
    },
        {'$match': {'discount': {'$gte': 0}}},
        {'$sort': {'difference': -1}},
        {'$limit': 3}
    ])
    for deal in deals:
        bestDeals.append(deal)

    return json_util.dumps(bestDeals)


fieldDataTypes = {
    'title': str,
    'description': str,
    'purchase_year': int,
    'price': float,
    'original_price': float,
    'location': float,
    'pics': str
}
@app.route("/update", methods=['POST'])
def updateTitle():
    """Update Fields"""

    key = request.form['key']
    value = request.form['value']

    if not key or key not in fieldDataTypes:
        return "Failure: Empty field key / Immutable key"
    if not value:
        return "Failure: Empty field value"

    if key in ['location', 'pics']:
        value = [fieldDataTypes[key](item) for item in value.split(',')]
    else:
        value = fieldDataTypes[key](value)

    id = request.form['id']

    print id, key, value

    update = collection.find_and_modify(
        query={'id': id},
        update={'$set': {key: value}},
        new=True
    )
    return json_util.dumps(update)

@app.route('/api')
def help():
    """API Documentation"""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


if __name__ == "__main__":
    app.run(debug=True)

