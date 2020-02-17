import pyodbc
import json
import pandas as pd
from pandasql import sqldf
from pandasql import load_births
from pandas import DataFrame
import numpy as np 
#import sqlalchemy


server = 'DESKTOP-FHC6TOI\\NAVDEMO'
database = 'Databaas'

#connection string definiëren
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                        SERVER=' + server + '; \
                             MARS_Connection=Yes; \
                            DATABASE=' + database +'; \
                                Trusted_Connection=yes;')





#connection cursor definiëren                        
cursor = cnxn.cursor()

#############################################################################
#SIMPELE QUERY + JSON STRING (NIET GEBRUIKT)
#############################################################################

#Query voor elke tabel
select_query_RelationContacts = '''SELECT * FROM Databaas.dbo.RelationContacts'''
select_query_Relations = '''SELECT * FROM Databaas.dbo.Relations'''
select_query_RelationTypes = '''SELECT * FROM Databaas.dbo.RelationTypes'''

#Query RelationContacts
cursor.execute(select_query_RelationContacts)
rows = cursor.fetchall()

rowarray_list = []
for row in rows:
    t = (row.ContactId
, row.ContactName)
    rowarray_list.append(t)
j = json.dumps(rowarray_list)
rowarrays_file = 'RelationContactsJSON.json'
f = open(rowarrays_file,'w')
print(j, file=f)

#Query Relations
cursor.execute(select_query_Relations)
rows = cursor.fetchall()

rowarray_list2 = []
for row in rows:
    t = (
 row.LeftContactId, row.RightContactId)
    rowarray_list2.append(t)
j = json.dumps(rowarray_list2)
rowarrays_file2 = 'RelationsJSON.json'
f = open(rowarrays_file2,'w')
print(j, file=f)


#Query RelationTypes
cursor.execute(select_query_RelationTypes)
rows = cursor.fetchall()

rowarray_list3 = []
for row in rows:
    t = (row.RelationTypeId, row.LeftContactTitle, 
         row.RightContactTitle)
    rowarray_list3.append(t)
j = json.dumps(rowarray_list3)
rowarrays_file3 = 'RelationTypesJSON.json'
f = open(rowarrays_file3,'w')
print(j, file=f)

#####################################################################################
#QUERY SOURCE & TARGET => DATAFRAME => UNIQUE NODES => CHANGE ST TO POSITIONAL INDEX#
#####################################################################################

#Query source target
select_query_ST = '''SELECT LeftContactId, RightContactId FROM Databaas.dbo.Relations'''
# cursor.execute(select_query_ST)
# for row in cursor:
#     print(f'row={row}')
# print()

# ST =[]
# for row in cursor:
#     ST.append(1)

# print(ST)

#df = DataFrame(resoverall.fetchall())
#df.columns = resoverall.keys()

#DATAFRAME#
df = pd.read_sql(select_query_ST, cnxn)
df.rename(columns={"LeftContactId":"source", "RightContactId":"target"}, inplace = True)

#UNIQUE NODES FOR POSITIION#
consolidated_index = pd.Index(df['source']
                      .append(df['target'])
                      .reset_index(drop=True).unique())
                                        
grouped_src_dst = df.groupby(["source","target"]).size().reset_index()

#LINK LIST WITH IDS#
temp_links_list = list(grouped_src_dst.apply(lambda row: {"source": row['source'], "target": row['target']}, axis=1))

#LINK LIST WITH POSITIONS#
links_list = []
for link in temp_links_list:
    record = { "source":consolidated_index.get_loc(link['source']),
     "target": consolidated_index.get_loc(link['target'])}
    links_list.append(record)


#LIST OF UNIQUE NODES (ID)#
nodes_list = []
for ip in consolidated_index:
        nodes_list.append(ip)


#PREPARED STATMEENT QUERY FOR NAMES#
placeholders = ','.join('?' for i in range(len(nodes_list)))
select_query_NAMES= '''
SELECT ContactId, ContactName FROM Databaas.dbo.RelationContacts WHERE ContactId IN (%s)
''' %placeholders

#NAMES DATAFRAME#
df_names = pd.read_sql(select_query_NAMES, cnxn, params=nodes_list)

#NAMES LIST OF TUPLES#
subset = df_names[['ContactId','ContactName']]
tuples = [tuple(x) for x in subset.to_numpy()]

#CHANGE NODE ID TO CORRESPONDING NAME#
new_nodes=[]
for node in nodes_list:
    for t in tuples:
        if(node == t[0] ):
            new_nodes.append(t[1])


#NODE LIST WITH NAMES TO DATAFRAME WITH NAMES#
new_nodes_df = pd.DataFrame(new_nodes, columns=['names'])

#NODE LIST DATAFRAME TO JSON OBJECT#
temp_nodes_list = list(new_nodes_df.apply(lambda row: {"name": row['names']}, axis=1))

#COMBINE NODES AND LINKS INTO ONE JSON OBJECT#
json_prep_named ={"nodes": temp_nodes_list, "links" : links_list}
json_dump_named = json.dumps(json_prep_named, indent=1, sort_keys=True, ensure_ascii=False)

print(json_dump_named)

#WRITE FULL JSON OBJECT#
filename_out = 'graph.json'
json_out = open(filename_out,'w', encoding='utf-8')
json_out.write(json_dump_named)
json_out.close()



#################################
#OLD JSON CONSTRUCTION(NOT USED)#
#################################

#Query nodes
select_query_N = '''SELECT ContactId FROM Databaas.dbo.RelationContacts'''
cursor.execute(select_query_N)

df = pd.read_sql(select_query_N, cnxn)
df.rename(columns={"ContactId":"name"}, inplace = True)

temp_nodes_list = list(df.apply(lambda row: {"name": row['name']}, axis=1))

json_prep = {"nodes": temp_nodes_list, "links": temp_links_list}
print(json_prep)

json_dump = json.dumps(json_prep, indent=1, sort_keys=True)

filename_out = 'export.json'
json_out = open(filename_out,'w')
json_out.write(json_dump)
json_out.close()









