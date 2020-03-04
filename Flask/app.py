import pyodbc
import sys
import json, random
#import numpy as np
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, Response
import urllib
#import time
#from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import or_

##### INIT FLASK APP #####
app = Flask(__name__)

##### DATABASE CONNECTION #####
paramsdb = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=vhuat.database.windows.net;PORT=1433;DATABASE=ucllDB;UID=AzureDB_admin;PWD=P@55w0rd')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % paramsdb
db = SQLAlchemy(app)


### HOLDS GRAPH IN CASE ITS REUSED ###
save_previous_graph = ""


##### MAP DB TABLES TO SQLALCHEMY OBJECTS #####
Base = automap_base()
Base.prepare(db.engine, reflect = True)
Relations = Base.classes.Relations
RelationContacts = Base.classes.RelationContacts
RelationTypes = Base.classes.RelationTypes



##### ALLOW CROSS ORIGIN REQUESTS #####
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


###### DEFAULT EMPTY LANDING PAGE ######
@app.route ('/', methods=['GET'])
def index():
    return render_template("index.html")


##### searchbar.js GETS JSON ONLOAD CONTAINING INFORMATION TO MATCH SEARCH-WORD TO #####
@app.route ('/id', methods=['GET'])
def searchData():
    select_searchdata = db.session.query(RelationContacts.ContactId, RelationContacts.ContactName,RelationContacts.ContactEmail,RelationContacts.ContactPhone,RelationContacts.CompanyName).all()
    searchdataJSON = parse_to_json(select_searchdata,["id","name","email","phone","companyname"])
    searchdataJSON = json.dumps(searchdataJSON)
    return searchdataJSON
 

##### QUERIES AND CONSTRUCTS GRAPH, ON SEARCH AND ON NODE-CLICK #####
@app.route ('/receivePersonID', methods=['GET', 'POST'])
def personID():

    data = request.get_json()

    ##### TRUE IF QUERY COMES FROM SEARCH BAR #####
    if isinstance(data, list):
        data = data[0]

        ### QUERY RELATIONS FROM GIVEN ID ###
        select_relations_by_id = db.session.query(Relations.RelationId, Relations.LeftContactId, Relations.RightContactId, Relations.RelationTypeId, RelationTypes.LeftContactTitle) \
        .filter(Relations.RelationTypeId == RelationTypes.RelationTypeId) \
        .filter(or_(Relations.LeftContactId == data['contactId'] , Relations.RightContactId == data['contactId'])).all() 
        
        
        ###SHOW NODES WITHOUT RELATIONS###
        if(select_relations_by_id) == [] :
            ### QUERY SINGLE CONTACT BY ID ###
            select_single_node = db.session.query(RelationContacts.ContactId, RelationContacts.ContactKind, RelationContacts.ContactName, RelationContacts.ContactEmail, RelationContacts.ContactPhone, RelationContacts.CompanyName) \
            .filter(RelationContacts.ContactId == data['contactId'] ).all()
            
            ### CONSTRUCT DICT/JSON FROM RESULT ###
            nodesJSONList = [param_as_dict(select_single_node[i],["ContactId", "ContactKind","ContactName", "ContactEmail", "ContactPhone", "CompanyName"]) for i in range(len(select_single_node))]
            linksListEmpty = []
            singleNodeJSON = {'links' :linksListEmpty ,'nodes':nodesJSONList}
            singleNodeJSON = jsonify(singleNodeJSON)
            return singleNodeJSON

        ##### SHOW MULTIPLE NODES #####
        return graphQuery(data,select_relations_by_id)

        
    ##### QUERY COMES FROM CLICKING ON NODE, SINGLE NODES WITHOUT RELATIONS WILL NOT BE SHOWN #####
    else:

        select_relations_by_id = db.session.query(Relations.RelationId, Relations.LeftContactId, Relations.RightContactId, Relations.RelationTypeId, RelationTypes.LeftContactTitle) \
        .filter(or_(Relations.LeftContactId == data['contactId'] , Relations.RightContactId == data['contactId'])) \
        .filter(Relations.RelationTypeId == RelationTypes.RelationTypeId).all()

        if select_relations_by_id == []:
            return save_previous_graph
        
        return graphQuery(data, select_relations_by_id)



##### GIVEN CONTACTID (DATA) AND ITS RELATIONS, QUERY ITS RELATED NODES AND CONSTRUCT COMPLETE GRAPH JSON #####
def graphQuery(data, select_relations_by_id):
        

        ### CONSTRUCT LIST OF DICTIONARIES OF GIVEN RELATIONS ###
        relationsJSONList = [param_as_dict(select_relations_by_id[i],["RelationId","source", "target", "RelationTypeId", "LeftContactTitle"]) for i in range(len(select_relations_by_id))]
        
        ### TAKE UNIQUE NODES FROM RELATIONS ###
        nodeset = set()
        for i in range(len(relationsJSONList)):
            nodeset.add(relationsJSONList[i]['source'])
            nodeset.add(relationsJSONList[i]['target'])

        ### QUERY UNIQUE NODES AND ADD TO LIST OF DICTS ###
        select_relationcontacts_by_id = db.session.query(RelationContacts.ContactId, RelationContacts.ContactKind, RelationContacts.ContactName, RelationContacts.ContactEmail, RelationContacts.ContactPhone, RelationContacts.CompanyName) \
        .filter(RelationContacts.ContactId.in_(nodeset)).all()

        contactsJSONList = [param_as_dict(select_relationcontacts_by_id[i],["ContactId", "ContactKind","ContactName", "ContactEmail", "ContactPhone", "CompanyName"]) for i in range(len(select_relationcontacts_by_id))]
        
        ### MERGE INTO GRAPH JSON ###
        graphJSON = {'links':relationsJSONList,'nodes':contactsJSONList}

        ### STORE CURRENT GRAPH ###
        save_previous_graph = graphJSON
        
        return graphJSON


##### FUNCTION TO PARSE QUERY RESULTS TO DICTIONARY(JSON) #####
def param_as_dict(data, names):
    result = dict()
    for itemIndex in range(len(names)):
        result[names[itemIndex]] = data[itemIndex]
    return result

##### SAME BUT ONLY USED ONCE IN SEARCHDATA FUNCTION #####
def parse_to_json(data,names):
    result = dict()
    for j in range(len(data)):
        item = data[j]
        persoon_dict = dict()
        for i in range(len(names)):
            persoon_dict[names[i]] = data[j][i]
        result[j] = persoon_dict
    return result


        


##### RETURNS JSON OF ENTIRE DATASET ##### 
# @app.route ('/all', methods=['GET'])
# def all():
#     a = time.time()
#     df = db.session.query(Relations.RelationId, Relations.LeftContactId, Relations.RightContactId, Relations.RelationTypeId).all()
#     #print(df)
#     #print(time.time() - a)
#     #a = time.time()
#     temp = [param_as_dict(df[i],["RelationId","source", "target", "RelationTypeId"]) for i in range(len(df))]
#     df = db.session.query(RelationContacts.ContactId, RelationContacts.CustomerId, RelationContacts.ClientId, RelationContacts.ContactName, RelationContacts.ContactEmail, RelationContacts.ContactPhone , RelationContacts.CompanyName, RelationContacts.ErpCode, RelationContacts.VatNumber, RelationContacts.FirstName, RelationContacts.LastName, RelationContacts.Discriminator, RelationContacts.MobilePhone , RelationContacts.Website, RelationContacts.Location, RelationContacts.SeniorAssistantEmail, RelationContacts.AssistantEmail, RelationContacts.Language, RelationContacts.ContactKind).all()
#     temp2 = [param_as_dict(df[i],["ContactId" ,"CustomerId" ,"ClientId" ,"ContactName" ,"ContactEmail" ,"ContactPhone" ,"CompanyName" ,"ErpCode" ,"VatNumber" ,"FirstName" ,"LastName" ,"Discriminator" ,"MobilePhone" ,"Website" ,"Location" ,"SeniorAssistantEmail" ,"AssistantEmail" ,"Language", "ContactKind"]) for i in range(len(df))]
#     jayson = {'links':temp,'nodes':temp2}
#     print(jayson)
#     return jsonify(jayson)
#     q3 = db.session.query(RelationContacts.ContactId, RelationContacts.ContactName,RelationContacts.
#     CustomerId, RelationContacts.ClientId, RelationContacts.ContactEmail, RelationContacts.ContactPhone, RelationContacts.CompanyName).filter(RelationContacts.ContactId.in_(set(nodelist))).all()




##### MAKES FILE RUNNABLE #####
if __name__ == '__main__':
	# run!
	app.run(host='0.0.0.0')