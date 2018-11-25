from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

"""sqlalchemy's engine provides connection funcationality to a variety of database implementations
    I've chosen to with and set up postgresql. However the code implementation will not vary"""
db_connect = create_engine('postgresql://main2:test1234@178.128.43.198:5432/pagerankdb')
#Initialise a flask application and use to handle the api for us
app = Flask(__name__)
api = Api(app)

class Rank(Resource):
    def get(self, pub_key):
        conn = db_connect.connect()
        query = conn.execute("SELECT pub_key, rank FROM rank WHERE pub_key = '%s'" % pub_key)
        result = {'data': [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class Ranks(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("SELECT pub_key, rank FROM rank")
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class ATRank(Resource):
    def get(self, pub_key):
        conn = db_connect.connect()
        query = conn.execute("SELECT * from rank WHERE pub_key = '%s'" % pub_key)
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class ATRanks(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("SELECT * FROM rank")
        result = {'data':[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

api.add_resource(Rank, '/ranks/<pub_key>')
api.add_resource(Ranks, '/ranks/')
api.add_resource(ATRank, '/atranks/<pub_key>')
api.add_resource(ATRanks, '/atranks/')

if __name__ == '__main__':
     app.run(port='5002')



