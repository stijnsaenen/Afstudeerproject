import pyodbc
import sys
import json, random
import pandas as pd
from pandasql import sqldf
from pandasql import load_births
from pandas import DataFrame
import numpy as np
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, Response
import urllib
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from flask_marshmallow import Marshmallow

#import sqlalchemy

app = Flask(__name__)
ma = Marshmallow(app)


paramsdb = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=vhuat.database.windows.net;PORT=1433;DATABASE=vhportal-prod-copy-2020-2-21-16-13;UID=AzureDB_admin;PWD=P@55w0rd')


#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % paramsdb
 

db = SQLAlchemy(app)

select_query_RelationContacts = '''SELECT * FROM ucllDB.dbo.RelationContacts'''
select_query_ST = '''SELECT LeftContactId, RightContactId FROM Databaas.dbo.Relations'''


RelationContacts = db.Table('RelationContacts', db.metadata, autoload=True, autoload_with=db.engine)


Base = automap_base()
Base.prepare(db.engine, reflect = True)
Relations = Base.classes.Relations
RelationContacts = Base.classes.RelationContacts
RelationTypes = Base.classes.RelationTypes

class RelationSchema(ma.ModelSchema):
    class Meta:
        model = Relations


from sqlalchemy.ext.declarative import DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

@app.route('/')
def index():

    result = db.session.query(RelationTypes).join(Relations, RelationTypes.RelationTypeId == Relations.RelationTypeId).count()

    return ""
#    return render_template('index.html', name='Joe')


@app.route ('/all', methods=['GET'])
def all():
    df = db.session.query(Relations).limit(30).all()

    # qqq = RelationSchema(many = True)
    # out = qqq.dump(df).data
    # print(jsonify({'relation' : out}))


    

    temp = json.dumps(df, cls=AlchemyEncoder)
    #print(json.loads(temp))
    # print(type(json.loads(temp)[0]))
    # dic = dict()

    # for entry in json.loads(temp):
    #     dic.update(entry)

    # print(dic)
    # print(type(dic))
    # print(type(temp))

    myString = temp[1:-1]
    #print(myString)

    jayson = "{\"relations\":" + temp + "}"


    print(jayson)
    print(type(json.loads(jayson)))


    return jayson

    nodelist=[]
    # for q in df:
    #     rel = []
    #     rel.append(q.LeftContactId)
    #     nodelist.append(q.LeftContactId)
    #     nodelist.append(q.RightContactId)
    #     rel.append(q.RightContactId)
    #     rel.append(q.RelationId)
    #     rel.append(q.RelationTypeId)
    #     relations.append(rel)
    # print(relations)
    # print(str(relations))
    # print(set(nodelist))
    
    # q2 = db.session.query(RelationContacts.ContactId,RelationContacts.ContactName).filter(RelationContacts.ContactId.in_(relations)).all()
    # print(q2)
    # for node in q2:
    #     print(node.ContactName)

    q3 = db.session.query(RelationContacts.ContactId, RelationContacts.ContactName,RelationContacts.
    CustomerId, RelationContacts.ClientId, RelationContacts.ContactEmail, RelationContacts.ContactPhone, RelationContacts.CompanyName).filter(RelationContacts.ContactId.in_(set(nodelist))).all()


    nodes = []
    for bo in q3:
        nodes.append([bo.ContactId, bo.ContactName,bo.
    CustomerId, bo.ClientId, bo.ContactEmail, bo.ContactPhone, bo.CompanyName])
    print(nodes)


    
   # df = pd.read_sql(query.statement, query.session.bind)
   #jseun = 
    #print(jsonify(df))
    # for r in res:
    #     print(r.LeftContactId, r.RightContactId)
    
    #return ""


# @app.route('/a')
# def quer():
#     results = db.session.query(RelationContact).all()
#     for r in results:
#         print(r.ContactId)

#     return ''
    


#  @app.route('/background_pro')
#  def background_pro():
#      try:
# #         word = request.args.get('word')
#     return result = ''
       


@app.route('/receiver', methods = ['POST'])
def worker():
    data = json.loads(request.data)
    print(data)
    result = ''

    for item in data:
        # loop over every row
        result += str(item['make']) + '\n'
    return result

if __name__ == '__main__':
	# run!
	app.run()

#@app.route('ContactName')
#def get_contact(ContactName):
#    contact = RelationContacts.query.filter
