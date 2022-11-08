# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter

with open('medical_conditions.json', "r") as json_file:
    MC = json.load(json_file)


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response
  

@app.route("/check_job", methods=['POST'])
def check_job():
    payload = request.get_json()
    job = payload["context"]["facts"]["occupation"]["value"]
    risk_job_list=["accountant","it_related", "call_center", "journalist"]
    if str(job) in risk_job_list:
      check_job = True
    else:
      check_job = False

    return query_response(value=check_job, grammar_entry=None)

@app.route("/age_category", methods=['POST'])
def age_category():
    payload = request.get_json()
    age = payload["context"]["facts"]["age"]["value"]
    if age > 40:
      age_category = "risk_group"
    else:
      age_category = "young"
      
    return query_response(value=age_category, grammar_entry=None)
  

@app.route("/blood_pressure", methods=['POST'])
def blood_pressure():
    payload = request.get_json()
    low_pressure = payload["context"]["facts"]["low_pressure"]["value"]
    high_pressure = payload["context"]["facts"]["high_pressure"]["value"]
    
    print (type(low_pressure),"\n",type(high_pressure))
    
    if low_pressure < 60:
      if high_pressure < 90:
        blood_pressure = "low"
    elif low_pressure > 90:
      if high_pressure > 140:
        blood_pressure = "high"
        
    return query_response(value=blood_pressure, grammar_entry=None)
  

@app.route("/lately", methods=['POST'])
def lately():
    payload = request.get_json()
    print(3*"\n", payload, 3*"\n")
    started = str(payload["context"]["facts"]["when_started"]["grammar_entry"])
    print(3*"\n", started, 3*"\n",)
    if "week" in started:
      lately = False
    else:
      lately = True

    return query_response(value=lately, grammar_entry=None)


@app.route("/diagnosis", methods=['POST'])
def diagnosis():
    symptom_list=[]
    payload = request.get_json()    
    for i in payload["context"]["facts"]:
          parameter = payload["context"]["facts"][i]
          if parameter != None:
            if parameter["sort"] == "symptom":
                  symptom_list.append(parameter["value"])
    print (symptom_list)
    for j in MC:

        if MC[j]["symptoms"] == symptom_list:
            # print(3*"\n", j, 3*"\n")
            diagnosis = str(j)
              
    return query_response(value=diagnosis, grammar_entry=None)
  

# conditions = {"Hypertension","Migrain","Bowel Inflammation","Drug-induced diarrhea","Stomach Ulcer Gallstones"}
@app.route("/inform", methods=['POST'])
def inform():
    payload = request.get_json()
    get_diagnosis = payload["context"]["facts"]["diagnosis"]["value"]
    diagnose = MC[get_diagnosis]["inform"]
    
    return query_response(value=diagnose, grammar_entry=None)
  

@app.route("/get_advice", methods=['POST'])
def get_advice():
    payload = request.get_json()
    get_diagnosis = payload["context"]["facts"]["diagnosis"]["value"]
    advice = MC[get_diagnosis]["advices"]

    return query_response(value=advice, grammar_entry=None)
  

@app.route("/prescribe", methods=['POST'])
def prescribe():
    payload = request.get_json()
    print(3*"\n", payload, 3*"\n")
    get_diagnosis = payload["context"]["facts"]["diagnosis"]["value"]
    medication = MC[get_diagnosis]["prescriptions"]
    if not medication :
      prescribe = "There is no prescriptions for your case of " + \
        get_diagnosis + ", just stick to what I have adviced you to do"
    else:
      prescribe = medication

    return query_response(value=prescribe, grammar_entry=None)
  




  
