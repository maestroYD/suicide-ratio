from mongoengine import connect
from flask import Flask, request, jsonify, url_for
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






@app.route("/Creating", methods=['POST'])
def save_information():
    parser = reqparse.RequestParser()
    parser.add_argument('country', type=str)
    args = parser.parse_args()

    country = args.get("country")


    if (os.path.isfile('suicide.csv') == False):

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


    if (os.path.isfile('education.csv') == False):

        url = "http://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=series:GER_56&DataMartId=UNESCO&Format=csv&c=2,3,5,7,9,10&s=ref_area_name:asc,time_period:desc"
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


    if (os.path.isfile('economy.csv') == False):

        url ="http://data.un.org/Handlers/DownloadHandler.ashx?DataFilter=grID:101;currID:USD;pcFlag:1&DataMartId=SNAAMA&Format=csv&c=2,3,5,6&s=_crEngNameOrderBy:asc,yr:desc"
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

    connect(
        host='mongodb://ass3:123456@ds229290.mlab.com:29290/ass3'
    )

    country_id = 0
    for t in Country.objects:
        if t.name == country.lower():
            flag = t.id
            return jsonify(country_id=flag), 202
        if t.id > country_id:
            country_id = t.id


    t1=[]
    flag_c=-1
    c = open("suicide.csv", "r")
    reader_c = csv.reader(c)
    for line in reader_c:
        if len(line)!=0:
            if line[0].replace(' ','').lower()==country.replace(' ','').lower():
                if line[2]=='Total':
                    flag_c=1
                    t1.append(suicide(int(line[1]),float(line[5])))

    if flag_c==-1:
        return jsonify("suicide data not found"), 404


    t2 = []
    flag_d=-1
    d = open("education.csv", "r")
    reader_d = csv.reader(d)
    for line in reader_d:
        if len(line) != 0:
            if line[0].replace(' ', '').lower() == country.replace(' ', '').lower():
                if line[2] == 'All genders':
                    flag_d=1
                    t2.append(education(int(line[1]), float(line[5])))

    if flag_d==-1:
        return jsonify("education data not found"), 404

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
        return jsonify("economy data not found"), 404

    t=Country(country_id+1,country.replace(' ','').lower(),t1,t2,t3)

    t.save()

    return jsonify(country_id=country_id+1), 200



@app.route("/country/<country>", methods=['GET'])
def search_country():
    parser = reqparse.RequestParser()
    parser.add_argument("country", type=str)
    args = parser.parse_args()

    target_country = args.get("country")

    return None

@app.route("/reigion/<region>", methods=['GET'])
def search_region():
    parser = reqparse.RequestParser()
    parser.add_argument("region", type=str)
    args = parser.parse_args()

    target_country = args.get("region")

    return None



if __name__ == '__main__':
    app.run(debug=True)