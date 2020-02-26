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
import time
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import inspect
app = Flask(__name__)


paramsdb = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=vhuat.database.windows.net;PORT=1433;DATABASE=vhportal-prod-copy-2020-2-21-16-13;UID=AzureDB_admin;PWD=P@55w0rd')

def obj_as_dict(obj):
    return {c.key: getattr(obj,c.key) for c in inspect(obj).mapper.column_attrs}

def param_as_dict(data, names):
    result = dict()
    for itemIndex in range(len(names)):
        result[names[itemIndex]] = str(data[itemIndex])
    return result

def parse_to_json(data,names):
    result = dict()
    for j in range(len(data)):
        item = data[j]
        persoon_dict = dict()
        for i in range(len(names)):
            persoon_dict[names[i]] = data[j][i]
        result[j] = persoon_dict
    return result

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % paramsdb
 
db = SQLAlchemy(app)


#RelationContacts = db.Table('RelationContacts', db.metadata, autoload=True, autoload_with=db.engine)



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


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response









@app.route ('/', methods=['GET'])
def index():
    df = db.session.query(RelationContacts.ContactId, RelationContacts.ContactName).limit(30).all()
    tem = parse_to_json(df,["id","name"])
    print(tem)
    temquotes = json.dumps(tem)
    tq = json.loads(temquotes)
    print(type(tem))
    print(type(temquotes))
    print(tq)
    print(type(tq))

    #result = db.engine.execute("select distinct contactId, contactName, CompanyName, ContactPhone, ContactEmail, VatNumber, ErpCode, Passport, MobilePhone from RelationContacts where contactId in(select RelationContacts.ContactIdfrom RelationContacts inner join relations ON (RelationContacts.ContactId = relations.LeftContactId)  inner join RelationContacts   ON (RelationContacts.ContactId = relations.RightContactId) inner join RelationTypes ON (RelationTypes.RelationTypeId = relations.RelationTypeId) where RelationContacts.ContactName like '%<zoekterm>%' or RelationContacts.CompanyName like '%la%' or RelationContacts.ContactPhone like '%la%' or RelationContacts.ContactEmail like '%la%' or RelationContacts.VatNumber like '%la%' or RelationContacts.ErpCode like '%la%' or RelationContacts.Passport like '%la%' or RelationContacts.MobilePhone like '%la%') union select distinct contactId, contactName, CompanyName, ContactPhone, ContactEmail, VatNumber, ErpCode, Passport, MobilePhone from RelationContacts where contactId in (select b.ContactId from RelationContacts a inner join relations y ON (a.ContactId = y.LeftContactId)  inner join RelationContacts b   ON (b.ContactId = y.RightContactId) inner join RelationTypes t ON (t.RelationTypeId = y.RelationTypeId) where b.ContactName like '%la%' or b.CompanyName like '%la%' or b.ContactPhone like '%la%' or b.ContactEmail like '%la%' or b.VatNumber like '%la%' or b.ErpCode like '%la%' or b.Passport like '%la%' or b.MobilePhone like '%la%') order by 1")
    #print(result)



    return render_template("index.html", idname = temquotes)


@app.route ('/all', methods=['GET'])
def all():
    a = time.time()
    df = db.session.query(Relations.RelationId, Relations.LeftContactId, Relations.RightContactId, Relations.RelationTypeId).limit(2).all()
    print(df)
    print(time.time() - a)
    a = time.time()
    temp = [param_as_dict(df[i],["RelationId","source", "target", "RelationTypeId"]) for i in range(len(df))]
    #temp = [obj_as_dict(df[i]) for i in range(len(df))]
    print(type(temp))
    print(time.time() - a)
    a = time.time()
    #myString = temp[1:-1]

    df = db.session.query(RelationContacts.ContactId, RelationContacts.CustomerId, RelationContacts.ClientId, RelationContacts.ContactName, RelationContacts.ContactEmail, RelationContacts.ContactPhone , RelationContacts.CompanyName, RelationContacts.ErpCode, RelationContacts.VatNumber, RelationContacts.FirstName, RelationContacts.LastName, RelationContacts.Discriminator, RelationContacts.MobilePhone , RelationContacts.Website, RelationContacts.Location, RelationContacts.SeniorAssistantEmail, RelationContacts.AssistantEmail, RelationContacts.Language).limit(0).all()
    print(time.time() - a)
    a = time.time() 
    #temp2  = [obj_as_dict(df[i]) for i in range(len(df))]
    temp2 = [param_as_dict(df[i],["ContactId" ,"CustomerId" ,"ClientId" ,"ContactName" ,"ContactEmail" ,"ContactPhone" ,"CompanyName" ,"ErpCode" ,"VatNumber" ,"FirstName" ,"LastName" ,"Discriminator" ,"MobilePhone" ,"Website" ,"Location" ,"SeniorAssistantEmail" ,"AssistantEmail" ,"Language"]) for i in range(len(df))]
    
    print(time.time() - a)
    a = time.time()
    #print(temp2)
    #print(type(temp2))
    print(time.time() - a)
    a = time.time()
    print(type(temp2))
    jayson = {'links':str(temp),'nodes':temp2}#"{\"links\":" + str(temp)   + " , \"nodes\":" + str(temp2)      + "}"
    print(time.time() - a)
    a = time.time()
    #print(jayson)
    #print(type(json))




    print(jayson)
    #print(type(json.loads(jayson)))
    return jsonify(jayson)

    q3 = db.session.query(RelationContacts.ContactId, RelationContacts.ContactName,RelationContacts.
    CustomerId, RelationContacts.ClientId, RelationContacts.ContactEmail, RelationContacts.ContactPhone, RelationContacts.CompanyName).filter(RelationContacts.ContactId.in_(set(nodelist))).all()


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


@app.route('/requestID', methods = ['GET'])
def requestID():
    data = request.data
    namelong = str(data)
    name = namelong[2:-1]
    print(name)
    
    q3 = db.session.query(RelationContacts.ContactId).filter(RelationContacts.ContactName == name).first()
    print(json.dumps(q3, cls=AlchemyEncoder))
    return json.dumps(q3, cls=AlchemyEncoder)
       


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
