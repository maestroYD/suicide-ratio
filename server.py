from mongoengine import connect
from flask import Flask, request, jsonify,url_for
from flask_restful import reqparse
from mongoengine import FloatField, StringField, IntField, Document, EmbeddedDocument, ListField, EmbeddedDocumentField
import requests
import os
from pathlib import Path
import csv
import xlrd
import zipfile
from bs4 import BeautifulSoup
from functools import wraps
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
import dicttoxml
from werkzeug.contrib.atom import AtomFeed
import datetime
import numpy as np
import urllib.request
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
import urllib


app = Flask(__name__)


class suicide(EmbeddedDocument):
    year = IntField(required=True, primary_key=True)
    value = FloatField(required=True)


    def __init__(self, year, value,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.value = value


class education(EmbeddedDocument):
    year = IntField(required=True, primary_key=True)
    value = FloatField(required=True)

    def __init__(self, year, value,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.value = value


class economy(EmbeddedDocument):
    year = IntField(required=True, primary_key=True)
    value = FloatField(required=True)

    def __init__(self, year, value,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.value = value


class Country(Document):
    id = IntField(required=True, primary_key=True)
    name= StringField(required=False,max_length=1000)
    suicide_collection=ListField(EmbeddedDocumentField(suicide))
    education_collection=ListField(EmbeddedDocumentField(education))
    economy_collection=ListField(EmbeddedDocumentField(economy))

    def __init__(self, id,name,suicide_collection=[],education_collection=[],economy_collection=[], *args, **values):
        super().__init__(*args, **values)
        self.id = id
        self.name=name
        self.suicide_collection=suicide_collection
        self.education_collection=education_collection
        self.economy_collection=economy_collection


def data_loading():

    #loading all country names
    country_list = []
    url = "https://developers.google.com/maps/coverage"
    html = urllib.request.urlopen(url)

    soup = BeautifulSoup(html, 'lxml')
    section = soup.find_all('td', class_='region notranslate')

    for tag in section:
        country = ""
        for tk in tag.contents[0].split():
            country += tk

        country_list.append(country.lower())
    #print(country_list)

    #remove old files if any
    for filename in ['suicide.csv', 'suicide.zip', 'education.csv', \
                    'education.zip', 'economy.csv', 'economy.zip']:
        if (os.path.isfile(filename)):
            os.remove(filename)


    #loading suicide data
    url = "http://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=series:SH_STA_SCIDE&DataMartId=SDGs&Format=csv&c=2,3,5,11,13,14&s=ref_area_name:asc,time_period:desc"
    r = requests.get(url)
    name='suicide.zip'
    with open(name, "wb") as code:
        code.write(r.content)

    zip_file = zipfile.ZipFile(name)
    for names in zip_file.namelist():
        zip_file.extract(names)
        extracted_path = Path(zip_file.extract(names))
        extracted_path.rename("suicide.csv")
    zip_file.close()


    #loading education data
    url = "http://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=series:GER_56;time_period:2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015&DataMartId=UNESCO&Format=csv&c=2,3,5,7,9,10&s=ref_area_name:asc,time_period:desc"
    r = requests.get(url)
    name='education.zip'
    with open(name, "wb") as code:
        code.write(r.content)

    zip_file = zipfile.ZipFile(name)
    for names in zip_file.namelist():
        zip_file.extract(names)
        extracted_path = Path(zip_file.extract(names))
        extracted_path.rename("education.csv")
    zip_file.close()


    #loading economy data
    url ="http://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=grID:101;currID:USD;pcFlag:true;yr:2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015&DataMartId=SNAAMA&Format=csv&c=2,3,5,6&s=_crEngNameOrderBy:asc,yr:desc"
    r = requests.get(url)
    name='economy.zip'
    with open(name, "wb") as code:
        code.write(r.content)

    zip_file = zipfile.ZipFile(name)
    for names in zip_file.namelist():
        zip_file.extract(names)
        extracted_path = Path(zip_file.extract(names))
        extracted_path.rename("economy.csv")
    zip_file.close()


    country_dict = {}
    country_dict_file = 'country_dict.txt'
    with open(country_dict_file, "r") as f:
        for line in f:
            country_name, country_sui, country_edu, country_eco = line.split()
            country_dict[country_name] = {"sui" : country_sui, \
                                        "edu" : country_edu, \
                                        "eco" : country_eco}

    #writing data to mongodb

    connect(
        host='mongodb://ass3:123456@ds229290.mlab.com:29290/ass3'
    )

    country_id = 1

    # for country in country_list[0:4]:
    for country in country_list:

        # print("Now loading - ", country, "seq = ", country_id)

        #country name normolization
        if country in country_dict.keys():
            country_sui = country_dict[country]["sui"]
            country_edu = country_dict[country]["edu"]
            country_eco = country_dict[country]["eco"]
        else:
            country_sui = country
            country_edu = country
            country_eco = country

        t1=[]
        flag_c=-1
        c = open("suicide.csv", "r")
        reader_c = csv.reader(c)
        for line in reader_c:
            if len(line)!=0:
                if line[0].replace(' ','').lower()==country_sui:
                    if line[2]=='Total':
                        flag_c=1
                        t1.append(suicide(int(line[1]),float(line[5])))

        # if flag_c==-1:
        #     print("suicide data not found for ", country)

        t2 = []
        flag_d=-1
        d = open("education.csv", "r")
        reader_d = csv.reader(d)
        for line in reader_d:
            if len(line) != 0:
                if line[0].replace(' ', '').lower() == country_edu:
                    if line[2] == 'All genders':
                        flag_d=1
                        t2.append(education(int(line[1]), float(line[5])))

        # if flag_d==-1:
        #     print("education data not found for ", country)

        t3 = []
        flag_e = -1
        e = open("economy.csv", "r")
        reader_e = csv.reader(e)
        for line in reader_e:
            if len(line) != 0:
                if line[0].replace(' ', '').lower() == country_eco:
                    flag_e = 1
                    t3.append(economy(int(line[1]), float(line[3])))

        # if flag_e == -1:
        #     print("economy data not found for ", country)

        t=Country(country_id, country, t1, t2, t3)

        t.save()

        country_id += 1


#whole db data
@app.route("/countries/worldwide", methods=['GET'])
def get_all():

    connect(
        host='mongodb://ass3:123456@ds229290.mlab.com:29290/ass3'
    )

    result = []
    return_dict={}

    for t in Country.objects():
        sum=0
        for s in t.suicide_collection:
            sum+=s.value
            
        s_ave=sum/4

        return_dict[t.id] = {}

        return_dict[t.id]["id"]=t.name
        return_dict[t.id]["avgration"]=s_ave

    result = list(return_dict.values())
    return jsonify(result), 200

#all data per country
@app.route("/countries/<country_name>", methods=['GET'])
def get_all_by_country(country_name):

    client = MongoClient('mongodb://ass3:123456@ds229290.mlab.com:29290/ass3')

    db = client['ass3']
    # print(db.collection_names()) 
    collection = db["country"]

    country_norm = country_name.replace(' ','').lower()

    if collection.find({"name" : country_norm }).count():
        for doc in collection.find({"name" : country_norm }):
            return jsonify(doc), 200
    else:
        return jsonify("Country doesn't exist"), 404


#external api for country general information
@app.route("/countries/info/<country_name>", methods=['GET'])
def search_country(country_name):

    link = "https://restcountries.eu/rest/v2/name/" + country_name

    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode())

    return jsonify(data), 200


#suicide data
@app.route("/countries/suicide/<country_name>", methods=['GET'])
def get_suicide(country_name):

    client = MongoClient('mongodb://ass3:123456@ds229290.mlab.com:29290/ass3')

    db = client['ass3']
    # print(db.collection_names()) 
    collection = db["country"]

    country_norm = country_name.replace(' ','').lower()

    if collection.find({"name" : country_norm }).count():
        for doc in collection.find({"name" : country_norm }):
            return jsonify(doc["suicide_collection"]), 200
    else:
        return jsonify("Country doesn't exist"), 404

#education data
@app.route("/countries/education/<country_name>", methods=['GET'])
def get_education(country_name):

    client = MongoClient('mongodb://ass3:123456@ds229290.mlab.com:29290/ass3')

    db = client['ass3']
    # print(db.collection_names()) 
    collection = db["country"]

    country_norm = country_name.replace(' ','').lower()

    if collection.find({"name" : country_norm }).count():
        for doc in collection.find({"name" : country_norm }):
            return jsonify(doc["education_collection"]), 200
    else:
        return jsonify("Country doesn't exist"), 404


#economy data
@app.route("/countries/economy/<country_name>", methods=['GET'])
def get_economy(country_name):

    client = MongoClient('mongodb://ass3:123456@ds229290.mlab.com:29290/ass3')

    db = client['ass3']
    # print(db.collection_names()) 
    collection = db["country"]

    country_norm = country_name.replace(' ','').lower()

    if collection.find({"name" : country_norm }).count():
        for doc in collection.find({"name" : country_norm }):
            return jsonify(doc["economy_collection"]), 200
    else:
        return jsonify("Country doesn't exist"), 404


#analysis part
@app.route("/countries/analysis/<country_name>", methods=['GET'])
def get_analyze(country_name):

    connect(
        host='mongodb://ass3:123456@ds229290.mlab.com:29290/ass3'
    )

    return_dict={}
    sum=0
    s_list=[]
    e_list=[]
    eco_list=[]
    for t in Country.objects():
        if t.name==country_name:

            for s in t.suicide_collection:
                sum+=s.value
                s_list.append(s.value)

            for e in t.education_collection:
                if e.year==2014 or e.year==2010 or e.year==2005 or e.year==2000:
                    e_list.append(e.value)

            for eco in t.economy_collection:
                if eco.year==2015 or eco.year==2010 or eco.year==2005 or eco.year==2000:
                    eco_list.append(eco.value)

    s_e=np.cov(s_list,e_list)[0][1]
    s_eco=np.cov(s_list,eco_list)[0][1]
    s_ave=sum/4

    return_dict["Country name"]=country_name
    return_dict["average suicide rate"]=s_ave
    return_dict["Correlation between suicide and education"]=s_e
    return_dict["Correlation between suicide and economy"]=s_eco

    return jsonify(return_dict), 200

if __name__ == '__main__':
    data_loading()
    app.run(debug=False)
