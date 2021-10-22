import requests
import time
import json
from datetime import datetime
import urllib
import math
import pytz
from requests.api import request
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timedelta

#devices = ["00:13:a2:00:41:d2:91:6a"]

devices = ["00:13:a2:00:41:d2:91:6a","00:13:a2:00:41:d2:91:1c","00:13:a2:00:41:d2:91:62","00:13:a2:00:41:d2:91:32","00:13:a2:00:41:d2:87:41","00:13:a2:00:41:d2:86:82",
                "00:13:a2:00:41:d2:91:4c","00:13:a2:00:41:d2:90:e5","00:13:a2:00:41:d2:91:12","00:13:a2:00:41:d2:91:25","consumowireless"]

BASE_URL = "https://industrial.api.ubidots.com"
VAR_LABEL = "promedio-semanal"
WEC_TOKEN = 'BBFF-tMsYAEzSPgbaiboO7zBUWZYwTpZAcP'
TIMEZONE = 'America/Santiago'
REQUESTS_FUNCTIONS = {"get": requests.get, "post": requests.post}
now = dt.now(tz=pytz.timezone(TIMEZONE))
headers= {"X-Auth-Token":WEC_TOKEN,"Content-Type":"application/json"}

#------------- INGRESAR RANGO DE HORAS -------------
HORAS = [21,22,23,0,1,2,3,4,5,6,7,8,9] # EJEMPLO: 21-9 horas
#----------------------------------------------------

def main():
    '''
    Main function - runs every time the function is executed.
    "args" is a dictionary containing both the URL params and the HTTP body (for POST requests).
    '''
    token = WEC_TOKEN
    if token is None:
        print("[ERROR] Please enter your Ubidots Token and device label to update in your args")
        return {"status": "error"}
    
    # Log the payload to the console, for debugging purposes. You may access the function's logs using
    # the option in the above header.
    inicio, fin = get_week_timerange() #(1633305600000, 1633910399000) #
    ahora = datetime.now()
    ts_ejecucion_function = int(datetime.timestamp(ahora)*1000)
    print("Timestamp de ejecucion del function: {}".format(ts_ejecucion_function))   
    if ts_ejecucion_function >= fin:
    #lista_horas(START, END)
        print("INFO Horas {}".format(HORAS))
        for device in devices:
            values = retrieve_single_variable_values(WEC_TOKEN, device,"pt", inicio, fin)
            #print(values)
            payload = filtro_hora_valor(values, HORAS)
            print("[INFO] Payload to send: {}".format(payload))
            if payload != None:
                response = update_device(device, payload, WEC_TOKEN)
                print("[INFO] POST request result:")
                print(response.status_code)
            else:
                print("[ERROR] No se ejecutó el calculo de promedio")
                response = None
        return {"status": "Promedios generados y enviados"}
    
    return {"status": "Ok"}
    

def update_device(device, payload, token):
    """
    updates a variable with a single dot
    """
    url = "{}/api/v1.6/devices/{}".format(BASE_URL, device)
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    response = create_request(url, headers, payload, attempts=5, request_type="post")
    return response

def create_request(url, headers, data, attempts, request_type):
    """
    Function to create a request to the server
    """
    request_func = REQUESTS_FUNCTIONS.get(request_type)
    kwargs = {"url": url, "headers": headers}
    if request_type == "post":
        kwargs["json"] = data

    try:
        req = request_func(**kwargs)
        print("[INFO] Request result: {}".format(req.text))
        status_code = req.status_code
        time.sleep(1)

        while status_code >= 400 and attempts < 5:
            req = request_func(**kwargs)
            print("[INFO] Request result: {}".format(req.text))
            status_code = req.status_code
            attempts += 1
            time.sleep(1)

        return req
    except Exception as e:
        print("[ERROR] There was an error with the request, details:")
        print(e)
        return None

def get_week_timerange():
    now_shifted = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_week = now.weekday()
    delta = td(days=day_week)
    delta2 = td(days=6-day_week, hours=23, minutes=59, seconds=59)
    init_ts = int((now_shifted - delta).timestamp()*1000)
    final_ts = int((now_shifted + delta2).timestamp()*1000)
    print(init_ts, final_ts)
    return init_ts, final_ts

def filtro_hora_valor(data, horas):
    dateTimeObj = datetime.now()
    resultado = list()
    curr_timestamp = round(datetime.timestamp(dateTimeObj)*1000)
    lista = list()
    results = data['results']
    print("[INFO] Cantidad de datos semana: {}".format(len(results)))
    resultado = [result for result in results if result['value'] > 0.0]
    #print(resultado)
    #return resultado
    print("[INFO] Datos mayores a cero {}".format(len(resultado)))    
    for result in resultado:
        timestamp = result['timestamp']
        dt_object = datetime.fromtimestamp(int(timestamp/1000), tz=pytz.timezone(TIMEZONE))
        hora = dt_object.hour
        #print(hora in horas, hora)
        if hora in horas:
            lista.append(float(result['value']))

    print("[INFO] Datos filtrados por rango de horas: {}".format(len(lista)))
    print("[INFO] Valores", lista)
    try:
        promedio = round(sum(lista)/len(lista),2)
        payload = {"prom":{"value":promedio, "timestamp":curr_timestamp}}
        return payload
    except Exception as e:
        print("[ERROR] Error con la peticion, detalles:")
        print(e)
        return None


def retrieve_single_variable_values(token, device_label, variable_label, inicio, fin):
    url= "{}/api/v1.6/devices/{}/{}/values/".format(BASE_URL, device_label, variable_label)
    headers= {"X-Auth-Token":token,"Content-Type":"application/json"}
    params = {"start":inicio, "end":fin, "page_size":3000}
    url = url + "?" + urllib.parse.urlencode(params)
    #print(url)
    #response = requests.get(url, headers=headers)
    response = create_request(url, headers, 5, "get")
    print("[INFO] Resultado del GET request {}".format(response.status_code))
    data = response.json()
    return data

main()
