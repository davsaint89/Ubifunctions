import requests
import time
import json



REQUESTS_FUNCTIONS = {"get": requests.get, "post": requests.post}

'''
Ubifunction that multiplies the last value of two variables into another value for an 
existing or non existing variable.

device1_label = device-label of origin device
var1 = variable-label of variable 1
var2 = variable-label of variable 2
resvar = variable-label of objective variable
'''

'''
variable definition example
'''
device = "internship-onboarding"
var1 = "battery"
var2 = "example-variable"
resvar = "set-variable-name"
token = "BBFF-McOre1vvNiQRc5nZCo9CSfhOAsVZQ8"

''' credential definition'''
URL = "https://industrial.api.ubidots.com"

def main(args):
    '''
    Main function - runs every time the function is executed.
    '''    
    if token is None:
        print("[ERROR] Please define your Ubidots Token")
        return {"status": "error"}

    if device is None:
        print("[ERROR] Please define the device-label where the data is to be extracted")
        return {"status": "error"}
    
    if var1 is None or var2 is None:
        print("[ERROR] Please define the labels of the variables to be multiplied")
        return {"status": "error"}

    if resvar is None:
        print("[ERROR] Please define the label of the objective variable")
        return {"status": "error"}
    
    print("[INFO] Variables to multiply: {} and {}".format(var1,var2), end=",")
    print("[INFO] Objective variable: {}".format(resvar), end=",")

    # Use the remaining parameters as payload
    req = update_device(device, token)

    # Prints the request result
    print("[INFO] Request result:")
    print(req.text)

    return {"status": "Ok", "result": req.json()}

def get_last_value_device(token,device):
    url= "{}/api/v2.0/devices/~{}/variables/?fields=label,lastValue".format(URL,device)
    headers= {"X-Auth-Token":token,"Content-Type":"application/json"}
    response = requests.get(url,headers=headers)
    return response


def update_device(device, token):
    """
    updates a variable with a single dot
    """

    url = "{}/api/v1.6/devices/{}".format(URL, device)
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

    req = create_request(url, headers, attempts=5, request_type="post")
    
    return req

def create_request(url, headers, attempts, request_type):
    """
    Function to create a request to the server
    """
    data = multiply(var1,var2,resvar)
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

def multiply(var1,var2,resvar):
    res = get_last_value_device(token,device)
    res_json = res.json()

    a = None
    b = None

    for i in range(len(res_json["results"])):
        if a and b != None:
            break
        elif res_json["results"][i]["label"]==var1:
            a = res_json["results"][i]["lastValue"]["value"]
        elif res_json["results"][i]["label"]==var2:
            b = res_json["results"][i]["lastValue"]["value"]


    c=a*b
        
    data = {resvar:c}
    return data