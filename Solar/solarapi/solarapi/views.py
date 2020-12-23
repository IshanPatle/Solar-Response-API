# importing essential libraries
import requests
import logging
import matplotlib.pyplot as plt
import numpy as np
import math
import json
import urllib.request
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render


def home(request):
    return HttpResponse(request, "home.html")

# function to return costing of residential area
def Costing(requests, lat, lng):

    api_key = 'GXgVWtRQg1aQH4UsgxdEPmx0VU7z04OmjRk9HrA2'
    api_url = 'https://developer.nrel.gov/api/utility_rates/v3.json?'

    link_request = '{}api_key={}&lat={}&lon={}'.format(api_url, api_key, lat, lng)
    response_costing = requests.get(link_request)

    resp_json_payload = response_costing.json()
    residential_val = resp_json_payload['outputs']['residential']
    return residential_val


# function to return latitude, longitude and area of mentioned address
def Solar(response, lat, lng, add):

    key_input = 'AIzaSyDUxPHHnzmRvyYxOBF5DYDnakPgWDks0uA'
    static_api_url = 'https://maps.googleapis.com/maps/api/staticmap?'
    zoom = 21
    length_input = 350
    height_input = 400

    location_input = add
    location_input = location_input.replace(" ", "+")
    query = '{}center={}&zoom={}&size={}x{}&maptype=satellite&scale=10&key={}'.format(static_api_url, location_input,
                                                                                      zoom, length_input,
                                                                                      height_input, key_input)

    print(query)
    location_input = location_input.replace(" ", "+")
    response = requests.get(
        ("https://maps.googleapis.com/maps/api/geocode/json?address=" + location_input + "&key={}").format(key_input))

    resp_json_payload = response.json()
    # lat = resp_json_payload['results'][0]['geometry']['location']['lat']
    # lng = resp_json_payload['results'][0]['geometry']['location']['lng']

    lat = float(lat)
    lng = float(lng)

    metersPerPx = (156543.03392 * (math.cos((float(lat) * math.pi)/ 180)) / (math.pow(2, zoom)))
    area = length_input * height_input * metersPerPx ** 2
    area_ft = round(area * 10.76391042, 2)

    resp_lat = "The Latitude of the mentioned address is: {}°".format(lat)
    resp_long = "The Longitude of the mentioned address is: {}°".format(lng)
    resp_area = "The predicted area for the address is {} sqft".format(area_ft)
    resp_query = "Please check the below link to view image: {}".format(query)

    kwh_cost = 0.5
    energy = area_ft*kwh_cost       #energy usage KWh per month
    val = float(Costing(requests, lat, lng))
    costing_result = float(energy) * float(val)

    data = {
    "_id": "5fc8d1e26cf6795e867cd3ef",
    "lat": lat,
    "lon": lng,
    "energy": {
        "wattvision": {
            "sensor_id": 0,
            "api_key": 0,
            "api_id": 0,
            "type": "rate",
            "start_time": "2013-01-18T21:50:00",
            "end_time": "2013-01-18T22:57:00"
        },
        "monthlyConsumption": energy,
        "monthlyCost": costing_result,
        "timeToPayoff": {
            "units": "years",
            "value": "10"
        },
        "paymentPerMonth": 100
    },
    "roof": {
        "tilt": 10,
        "usableArea": {
            "units": "sqft",
            "value": area_ft
        },
        "direction": 0,
        "elevation": {
            "units": "ft",
            "value": 20
        }
    },
    "__v": 0
    }

    with open("data_file.json", "w") as file_write:
        json.dump(data, file_write)

    json_str = json.dumps(data, indent=1)
    return HttpResponse(json_str)

#testing address
# Solar('11002 Bee Canyon Access Rd, Irvine, CA 92602, United States', 21, 350, 500)

#http://127.0.0.1:8000/?add=11002+Bee+Canyon+Access+Rd,+Irvine,+CA+92602,+United%20States&lat=33.7171859197085&lng=-117.7110931302915
#http://127.0.0.1:8000/Solar/33.7171859197085/-117.7110931302915/11002+Bee+Canyon+Access+Rd,+Irvine,+CA+92602,+United%20States/

