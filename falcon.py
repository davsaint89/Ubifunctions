import requests
import time
import json
from datetime import datetime

"""
creen un código que extraiga el último valor de estas 12 variables, los promedie y los envíe a una nueva variable.
"""

BASE_URL = "https://industrial.api.ubidots.com"
DEV_LABEL = "ubifunction-temperatura"
VAR_LABEL = "promedio-temperatura-bodegas"

devices = {

    "arduinonano":"temperatura1", 
    "2bff64546fe987a612080151af5f7927":"humidity", 
    "sigfoxprueba1":"temperatura"
}

metrix_devices = {

    "471bbd48001c003a":"temperatura",
    "471bbd48002b003b":"temperatura",
    "471bbd4800510034":"temperatura",
    "47eabd48003a0034":"temperatura",
    "47eabd4800420034":"temperatura",
    "47fabd48001e004c":"temperatura",
    "47fabd4800220045":"temperatura",
    "47fabd4800230044":"temperatura",
    "47fabd4800290042":"temperatura",
    "47fabd48004c0042":"temperatura",
    "47fabd4800530044":"temperatura",
    "47fb558000230037":"temperatura"
}

METRIX_TOKEN = 'BBFF-FDnScISElqhq3YbuEg5UTcTKdfJzH1'
token = 'BBFF-hLcdSZjx4mvM078IcgXWsKUG4AdCki'

def get_last_value_device(token,device):
    url= "{}/api/v2.0/devices/~{}/variables/?fields=lastValue".format(BASE_URL,device)
    headers= {"X-Auth-Token":token,"Content-Type":"application/json"}
    response = requests.get(url,headers=headers)
    return response.json()


def send_data_to_new_device(data, device_label, attempts=1):
    headers= {"X-Auth-Token":token,"Content-Type":"application/json"}
    url = "{}/api/v1.6/devices/{}".format(BASE_URL, device_label)
    try:
        response = requests.post(url,headers=headers, data=json.dumps(data))
        status_code = response.status_code
        while status_code >= 400 and attempts < 5:
            response = requests.get(url,headers=headers)
            print("[INFO] Request result: {}".format(response.text))
            status_code = response.status_code
            attempts += 1
            time.sleep(1)
        return response.json()
    except Exception as e:
        print("[ERROR] There was an error with the request, details:")
        print(e)
        return None

def get_last_value_from_variable(device, variable, attempts = 0):
    url = "{}/api/v2.0/devices/~{}/variables/~{}/?fields=name,lastValue".format(BASE_URL, device, variable)
    headers= {"X-Auth-Token":METRIX_TOKEN,"Content-Type":"application/json"}
    try:
        response = requests.get(url,headers=headers)
        status_code = response.status_code
        while status_code >= 400 and attempts < 5:
            response = requests.get(url,headers=headers)
            print("[INFO] Request result: {}".format(response.text))
            status_code = response.status_code
            attempts += 1
            time.sleep(1)
        last_value = response.json()['lastValue']['value']
        value_timestamp = response.json()['lastValue']['timestamp']
        return last_value, value_timestamp
    except Exception as e:
        print("[ERROR] There was an error with the request, details:")
        print(e)
        return None

def calculate_average(devices):
    dateTimeObj = datetime.now()
    timestamp = round(datetime.timestamp(dateTimeObj)*1000)
    lecturas = list()
    payload = {}
    for device_label, variable_label in devices.items():
        lectura, time_s = get_last_value_from_variable(device_label, variable_label)
        diff = round(((timestamp - time_s)/3600000),2) # diferencia en horas
        print(diff)
        if diff < 0.9:
            lecturas.append(lectura)
        
    print(lecturas)
    average = sum(lecturas)/len(lecturas)
    print(average)
    payload = {VAR_LABEL: {"value":round(average,2), "timestamp":timestamp}}
    return payload


payload = calculate_average(metrix_devices)
print(send_data_to_new_device(payload, DEV_LABEL))

#print(get_last_value_from_variable("arduinonano", "temperatura1"))
