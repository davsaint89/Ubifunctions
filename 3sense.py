from datetime import datetime as dt
from datetime import timedelta as td
import pytz
import time
import requests
# current date and time

"""
 https://www.programiz.com/python-programming/datetime/timestamp-datetime
"""
BASE_URL = "https://industrial.api.ubidots.com"
REQUESTS_FUNCTIONS = {"get": requests.get, "post": requests.post}
TIMEZONE = "America/Bogota"
DATE_EVENT = "20/10/2020:15:33:02" #iNGRESE LA FECHA DEL EVENTO
DELAY = 365 # iNGRESE EL RETARDO EN DÌAS PARA EL DISPARO DE LA ALARMA
TOKEN = "BBFF-hLcdSZjx4mvM078IcgXWsKUG4AdCki"

def main():
    now = dt.now(tz=pytz.timezone(TIMEZONE))  
    date_entered = dt.strptime(DATE_EVENT,"%d/%m/%Y:%H:%M:%S")
    future_date = date_entered + td(days=DELAY)  
    print(future_date)
    future_date_timestamp = int(dt.timestamp(future_date))
    print("[INFO] Fecha del evento: {}".format(date_entered))
    print("[INFO] Fecha actual: {}".format(now))
    print("[INFO] Fecha disparo de la Alarma: {}".format(future_date))
    current_date_timestamp = int(dt.timestamp(now))

    diff = current_date_timestamp -future_date_timestamp
    print(diff)
    if diff > 0 and diff < 200:
        print(current_date_timestamp, future_date_timestamp)
        if  current_date_timestamp >= future_date_timestamp:
            print("Alarma activada")
        else:
            print("Normal")


#print("dentro de un año será {}".format(now + timedelta(days=365)))


#print("timestamp =", timestamp)

#print(timedelta(days=365, hours=0, minutes=0))


def update_device(device, payload, token):
    """
    updates a variable with a single dot
    """

    url = "{}/api/v1.6/devices/{}".format(BASE_URL, device)
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

    req = create_request(url, headers, payload, attempts=5, request_type="post")
    
    return req

def create_request(url, headers, attempts, request_type, data=None):
    """
    Makes an API request to the server
    """
    request_func = getattr(requests, request_type)
    kwargs = {"url": url, "headers": headers}
    if request_type == "post" or request_type == "patch":
        kwargs["json"] = data
    try:
        response = request_func(**kwargs)
        status_code = response.status_code
        time.sleep(1)
        while status_code >= 400 and attempts < 5:
            response = request_func(**kwargs)
            status_code = response.status_code
            attempts += 1
            time.sleep(1)
        return response
    except Exception as e:
        print("[ERROR] There was an error with the request, details:")
        print(e)
        return None
