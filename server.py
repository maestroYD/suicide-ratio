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
<<<<<<< HEAD
import numpy as np
=======
import urllib.request
import json
from pymongo import MongoClient

from bs4 import BeautifulSoup
import urllib
>>>>>>> 9ac34c8b332a1288bd09f1ad2dd1c3f4701e5384


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
        self.suicide_collection = suicide_collection
        self.education_collection=education_collection
        self.economy_collection=economy_collection


def data_loading():

    #country is an dictionary

    # client = MongoClient('mongodb://ass3:123456@ds229290.mlab.com:29290/ass3')

    # db = client['ass3']
    # print(db.collection_names()) 
    # collection = db["country"]

    # country_norm = country.replace(' ','').lower()

    # if collection.find({"name" : country_norm }).count():
    #     for doc in collection.find({"name" : country_norm }):
    #         return jsonify(doc), 200

    #country name filter
    #more to be done
    # if country.lower() in ["united states", "united states of america", "usa", "america", "us"]:
    #     country_suicide = "unitedstatesofamerica"
    #     country_education = "unitedstatesofamerica"
    #     country_economy = "unitedstates"
    # elif country.lower() in ["russia", "russian federation"]:
    #     country_suicide = "russianfederation"
    #     country_education = "russianfederation"
    #     country_economy = "russianfederation"
    # elif country.lower() in ["uk", "united kindom", "great britain"]:
    #     country_suicide = "unitedkingdomofgreatbritainandnorthernireland"
    #     country_education = "unitedkingdomofgreatbritainandnorthernireland"
    #     country_economy = "unitedkingdomofgreatbritainandnorthernireland"
    # elif country.lower() in ["south korea", "democratic people's republic of korea"]:
    #     country_suicide = "democraticpeople'srepublicofkorea"
    #     country_education = "democraticpeople'srepublicofkorea"
    #     country_economy = "democraticpeople'srepublicofkorea"
    # else:
    #     country_suicide = country
    #     country_education = country
    #     country_economy = country

    # for c in countries:
    #     print(c.name)s

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

    #writing data to mongodb
    connect(
        host='mongodb://ass3:123456@ds229290.mlab.com:29290/ass3'
    )

    country_id = 0
    for country in country_list:

        print("Now loading - ", country, "seq = ", country_id)

        # for t in Country.objects:
        #     if t.name == country.replace(" ","").lower():
        #         flag = t.id
        #         return jsonify(country_id=flag), 202
        #     if t.id > country_id:
        #         country_id = t.id

        t1=[]
        flag_c=-1
        c = open("suicide.csv", "r")
        reader_c = csv.reader(c)
        for line in reader_c:
            if len(line)!=0:
                if line[0].replace(' ','').lower()==country:
                    if line[2]=='Total':
                        flag_c=1
                        t1.append(suicide(int(line[1]),float(line[5])))

        if flag_c==-1:
            print("suicide data not found for ", country)

        t2 = []
        flag_d=-1
        d = open("education.csv", "r")
        reader_d = csv.reader(d)
        for line in reader_d:
            if len(line) != 0:
                if line[0].replace(' ', '').lower() == country:
                    if line[2] == 'All genders':
                        flag_d=1
                        t2.append(education(int(line[1]), float(line[5])))

        if flag_d==-1:
            print("education data not found for ", country)

        t3 = []
        flag_e = -1
        e = open("economy.csv", "r")
        reader_e = csv.reader(e)
        for line in reader_e:
            if len(line) != 0:
                if line[0].replace(' ', '').lower() == country.replace(' ', '').lower():
                    flag_e = 1
                    t3.append(economy(int(line[1]), float(line[3])))

        if flag_e == -1:
            print("economy data not found for ", country)

        t=Country(country_id+1, country, t1, t2, t3)

<<<<<<< HEAD
############changed new################
@app.route("/get_analyze/<country_name>", methods=['GET'])
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













=======
        t.save()
>>>>>>> 9ac34c8b332a1288bd09f1ad2dd1c3f4701e5384

        country_id += 1

        #return jsonify(country_id=country_id+1), 200


#external api for country general information
@app.route("/Countries/<country>", methods=['GET'])
def search_country(country):

    link = "https://restcountries.eu/rest/v2/name/" + country

    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode())

    return jsonify(data), 200


@app.route("/get_analyze/<country_name>", methods=['GET'])
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
