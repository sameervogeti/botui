import json

from flask import render_template, request, make_response,jsonify
import dialogflow
from app import app
from google.protobuf.json_format import MessageToJson
import os
import timeit
from forecast import Forecast, validate_params


log = app.logger

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    projectpath = request.form['projectFilepath']
    # your code
    # return a response
    print(projectpath)
    return "thanks"


@app.route('/login', methods=['GET', 'POST'])
def login():
   start = timeit.default_timer()
   message = None
   if request.method == 'POST':
        input_question = request.form['mydata']
        print(input_question)
        start = timeit.default_timer()
        while(timeit.default_timer()-start<2):
             os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<Path to Service>>"
             final_json_result = detect_intent_texts("dialogflow-poc-268718", "abcd", [input_question], "en-US")
             return final_json_result


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    for text in texts:
        start = timeit.default_timer()
        text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(session=session, query_input=query_input)
        print("**************")
        print(timeit.default_timer()-start)
        jsonObj = MessageToJson(response.query_result)
        print(jsonObj)
        j = json.loads(jsonObj)
        try:
            action = j['action']
        except AttributeError:
            return 'json error'

        if action == 'weather':
            res = weather(j)
            final_json_result = json.dumps(res)
            return final_json_result
        elif action == 'weather.activity':
            res = weather_activity(j)
            final_json_result = json.dumps(res)
            return final_json_result
        elif action == 'weather.condition':
            res = weather_condition(j)
            final_json_result = json.dumps(res)
            return final_json_result
        elif action == 'weather.outfit':
            res = weather_outfit(j)
            final_json_result = json.dumps(res)
            return final_json_result
        elif action == 'weather.temperature':
            res = weather_temperature(j)
            final_json_result = json.dumps(res)
            return final_json_result
        else:
            fulfillment_message_list = j['fulfillmentMessages']
            print(len(fulfillment_message_list))

            data = {}
            for i in range(len(fulfillment_message_list)):
                try:
                    print(fulfillment_message_list[i]['text']['text'][0])
                    data[i] = fulfillment_message_list[i]['text']['text'][0]
                except:
                    pass

            final_json_result = json.dumps(data)
            return final_json_result

def weather(req):
    """Returns a string containing text with a response to the user
    with the weather forecast or a prompt for more information

    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    parameters = req['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(parameters)
    if error:
        return error

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # If the user requests a datetime period (a date/time range), get the
    # response
    if forecast.datetime_start and forecast.datetime_end:
        response = forecast.get_datetime_period_response()
    # If the user requests a specific datetime, get the response
    elif forecast.datetime_start:
        response = forecast.get_datetime_response()
    # If the user doesn't request a date in the request get current conditions
    else:
        response = forecast.get_current_response()

    return response


def weather_activity(req):
    """Returns a string containing text with a response to the user
    with a indication if the activity provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, activity and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the activities listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['parameters'])
    if error:
        return error

    # Check to make sure there is a activity, if not return an error
    if not forecast_params['activity']:
        return 'What activity were you thinking of doing?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # get the response
    return forecast.get_activity_response()


def weather_condition(req):
    """Returns a string containing a human-readable response to the user
    with the probability of the provided weather condition occurring
    or a prompt for more information

    Takes a city, condition and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the conditions listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['parameters'])
    if error:
        return error

    # Check to make sure there is a activity, if not return an error
    if not forecast_params['condition']:
        return 'What weather condition would you like to check?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # get the response
    return forecast.get_condition_response()


def weather_outfit(req):
    """Returns a string containing text with a response to the user
    with a indication if the outfit provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, outfit and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the outfits listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['parameters'])
    if error:
        return error

    # Validate that there are the required parameters to retrieve a forecast
    if not forecast_params['outfit']:
        return 'What are you planning on wearing?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    return forecast.get_outfit_response()


def weather_temperature(req):
    """Returns a string containing text with a response to the user
    with a indication if temperature provided is consisting with the
    current weather or a prompt for more information

    Takes a city, temperature and (optional) dates.  Temperature ranges for
    hot, cold, chilly and warm can be configured in config.py
    uses the template responses found in weather_responses.py as templates
    """

    parameters = req['parameters']

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(parameters)
    if error:
        return error

    # If the user didn't specify a temperature, get the weather for them
    if not forecast_params['temperature']:
        return weather(req)

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    return forecast.get_temperature_response()

