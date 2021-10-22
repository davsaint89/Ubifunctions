import requests
import json
import time
import datetime

BASE_URL = "https://industrial.api.ubidots.com"

REQUESTS_FUNCTIONS = {"get": requests.get, "post": requests.post}

def main(args):
    print(args)
    print(args['data'])
    '''
    Main function - runs every time the function is executed.
    "args" is a dictionary containing both the URL params and the HTTP body (for POST requests).
    '''
    token = "BBFF-xtXwnheOPATcbDbiakqY1nBgnCzenQ"
    device_t = args.get('asset_id')
    device = device_t[1:]

    print(device)

    if token is None or device is None:
        print("[ERROR] Please send your Ubidots Token and device label to update in your args")
        return {"status": "error"}
    
 
    del args['entry_received']

    string = args['data']
    message = string.split(',')

    mapa = {

        "O":"signal_strength",
        "A":"significant_wave_height",
        "B":"maximum_wave_height",
        "C":"peak_wave_period",
        "D":"mean_wave_period",
        "E":"peak_wave_direction",
        "F":"temperature",
        "AG":"microchip_regulated_voltage",
        "AE":"rtc_battery_voltage",
        "AF":"average_wave_height",
        "AD":"software_version",
        "AH":"sd_card_capacity_remaining",
        "LF":"line_feed"
    }

    payload = get_payload(message, mapa)
    print("[INFO] Payload to send: {}".format(payload))
    res = update_device(device, payload, token)
    print("[INFO] Request result:")
    print(res.text)
    return {"status": "Ok", "result": res.json()}


def get_data(input, key1, key2):
    for item in input:
        pair = item.split(';')
        if len(pair) == 2:
            key = pair[0]
            value = pair[1]
            if key == key1:
                data1 = value
            if key == key2:
                data2 = value
    return data1, data2

def calculate_timestamp(fecha, hora):
    date_s = fecha + ":" + hora
    date_obj = time.mktime(datetime.datetime.strptime(date_s, "%d/%m/%Y:%H:%M:%S").timetuple())
    return round(date_obj * 1000)


def get_payload(input, mapa):
    payload = {}
    fecha, hora = get_data(input, "K", "J")
    lat, lng = get_data(input, "G", "H")
    timestamp = calculate_timestamp(fecha, hora)
    for item in input:
        pair = item.split(';')
        if len(pair) == 2:
            key = pair[0]
            value = pair[1]
            if key in mapa:
                payload[mapa[key]] = {"value":float(value), "timestamp":timestamp}
    payload["position"] = {"value":1, "timestamp":timestamp, "context":{"lat":float(lat), "lng":float(lng)}}
    return payload


def update_device(device, payload, token):
    """
    updates a variable with a single dot
    """

    url = "{}/api/v1.6/devices/{}".format(BASE_URL, device)
    print(url)
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

    res = create_request(url, headers, payload, attempts=5, request_type="post")
    
    return res




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





