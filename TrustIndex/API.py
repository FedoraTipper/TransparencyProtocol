from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

db_connect = create_engine('postgresql://main2:test1234@178.128.43.198:5432/pagerankdb')
app = Flask(__name__)
api = Api(app)


class Rank(Resource):
    def get(self, pub_key):
        conn = db_connect.connect()
        query = conn.execute("select * from rank where pub_key = '%s'" % pub_key)
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

api.add_resource(Rank, '/rank/<pub_key>') # Route_1

if __name__ == '__main__':
     app.run(port='5002')

