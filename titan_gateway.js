// Import the 'axios' library so we can make HTTP request from the function
const axios = require('axios');

// Ubidots Access Credentials 
var ubidotsToken = 'BBFF-w5C6NlsQRkbuB9WyqFm5LAVkUDpkGE';

// Main function - runs every time the function is executed.
// "args" is a dictionary containing both the URL params and the HTTP body (for POST requests).
async function main(args) {

console.log(args);

  // Grab the token and device label from URL parameters, then erase them from the args dictionary
  //var device_label = 'demo';
  // delete args['token'];
  // delete args['device'];

  // Use the remaining parameters as payload
  var d = new Date(args['TS']);
  var device_label = 'demo';//args['IMEI'];
  var timeStamp = d.getTime();
  //console.log(timeStamp)
  var nJson = {};
  delete args['TS'];
  delete args['IMEI'];
  delete args['TYPE'];
  delete args['ID'];
  delete args['A'];
  delete args['ST'];
  delete args['N'];
  delete args['P'];

  for(var llave in args){
      if(args[llave] < 1.0E-10)
      {
        args[llave] = 0.0;
      }
      nJson[llave] = {'value': args[llave],'timestamp': timeStamp};
  }


  var payload = JSON.stringify(nJson);

  // Log the payload to the console, for debugging purposes. You may access the function's logs using
  // the option in the above header.
  console.log(payload);

  // Send the payload to Ubidots
  var response = await ubidots_request(device_label, payload);

  // Log Ubidots response to the console
  console.log(response);

  // Pass Ubidots' API response as the function's reponse
  //return args, device_label;
  return response;
}

// This function builds an HTTP POST request to Ubidots
async function ubidots_request(device_label, body) {
  let config = {
    method: 'post',
    url: 'https://industrial.api.ubidots.com/api/v1.6/devices/' + device_label,
    data: body,
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': ubidotsToken
    }
  }
  const response = await axios.request(config);
  return response.data;
}