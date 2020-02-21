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

#import sqlalchemy

app = Flask(__name__)


paramsdb = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=vhuat.database.windows.net;PORT=1433;DATABASE=vhportal-prod-copy-2020-2-21-16-13;UID=AzureDB_admin;PWD=P@55w0rd')


#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % paramsdb
 

db = SQLAlchemy(app)

select_query_RelationContacts = '''SELECT * FROM ucllDB.dbo.RelationContacts'''
select_query_ST = '''SELECT LeftContactId, RightContactId FROM Databaas.dbo.Relations'''


RelationContacts = db.Table('RelationContacts', db.metadata, autoload=True, autoload_with=db.engine)



# class RelationContacts(db.Model):
#     ContactId= db.Column(db.Integer, primary_key=True)
#     ContactName = db.Column(db.String(50))
#     ContactKind = db.Column(db.Integer)
#     CustomerId = db.Column(db.Integer)
#     ClientId = db.Column(db.Integer)
#     ContactEmail = db.Column(db.String(50))
#     ContactPhone = db.Column(db.Integer)
#     CreatedDateUtc = db.Column(db.String(50))
#     ModifiedDateUtc = db.Column(db.String(50))
#     CompanyName = db.Column(db.String(50))

# class Relations(db.Model):
#     RelationId= db.Column(db.Integer, primary_key=True)
#     RelationTypeId = db.Column(db.Integer)
#     LeftContactId = db.Column(db.Integer)
#     RightContactId = db.Column(db.Integer)
#     CreatedDateUtc = db.Column(db.String(50))
#     ModifiedDateUtc = db.Column(db.String(50))
#     HideFromCustomer = db.Column(db.Boolean)
#     RelationValidationStatus = db.Column(db.Integer)

# class RelationTypes(db.Model):
#     RelationTypeId= db.Column(db.Integer, primary_key=True)
#     DisplayName = db.Column(db.String(50))
#     LeftContactTitle = db.Column(db.String(50))
#     RightContactTitle = db.Column(db.String(50))
#     CreatedDateUtc = db.Column(db.String(50))
#     ModifiedDateUtc = db.Column(db.String(50))
#     IsSystem = db.Column(db.Boolean)
#     SystemName = db.Column(db.String(50))
#     IsPepRelevant = db.Column(db.Boolean)


    


Base = automap_base()
Base.prepare(db.engine, reflect = True)
Relations = Base.classes.Relations
RelationContacts = Base.classes.RelationContacts
RelationTypes = Base.classes.RelationTypes


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
    request.data[]
    df = db.session.query(Relations).all()
    temp = json.dumps(df, cls=AlchemyEncoder)
    print(temp)
    return json.dumps(df, cls=AlchemyEncoder)
    relations = []
    nodelist=[]
    for q in df:
        rel = []
        rel.append(q.LeftContactId)
        nodelist.append(q.LeftContactId)
        nodelist.append(q.RightContactId)
        rel.append(q.RightContactId)
        rel.append(q.RelationId)
        rel.append(q.RelationTypeId)
        relations.append(rel)
    print(relations)
    print(str(relations))
    print(set(nodelist))
    
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



    name id
        
    
    return jsonify(result = str(relations))

    
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
