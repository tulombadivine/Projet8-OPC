import json
import logging
import re
from datetime import datetime

import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

from res_france_toolkit.dailytracker import DailyTrackerDB

app = Flask(__name__)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application",
        'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
    },
)

app.register_blueprint(swaggerui_blueprint)


@app.route('/')
def index():
    return render_template('home.html')


db = DailyTrackerDB(dev=True)


@app.route('/events/<int:identity>', methods=['GET'])
def GetEvent(identity):
    overview = True
    try:
        result = db.get_event(identity, overview).squeeze()
    except Exception as e:
        logging.error(f"An error occurred while fetching events: {str(e)}")
        return jsonify({"message": f"Failed to fetch events: {str(e)}", "data": None}), 500

    try:
        if result.empty:
            return jsonify({"message": "No Events Found!", "data": None}), 404
    except Exception as e:
        logging.error(f"An error occurred while checking if result is empty: {str(e)}")
        return jsonify({"message": f"Failed to check if result is empty: {str(e)}", "data": None}), 500

    try:
        data = json.loads(result.to_json())
        return jsonify({"message": "Success", "data": data}), 200
    except json.JSONDecodeError:
        logging.error("Failed to parse result to JSON")
        return jsonify({"message": "Failed to parse result to JSON", "data": None}), 500


@app.route('/events/insert', methods=['POST'])
def insert_event():
    data = request.get_json()

    if data is None:
        return jsonify({"message": "Invalid JSON data received"}), 400

    try:
        if not isinstance(data, dict) or 'data' not in data or not isinstance(data['data'], dict):
            raise ValueError("Invalid JSON format. Expected a dictionary with 'data' key containing another dictionary")
    except ValueError as ve:
        return jsonify({"message": f"Error in JSON structure: {str(ve)}"}), 400

    inner_data = data['data']

    try:
        result = db.insert_dt(inner_data)
        return jsonify({"message": "Event inserted successfully", "inserted_id": result}), 201
    except Exception as e:
        return jsonify({"message": f"Failed to insert event: {str(e)}"}), 500


@app.route('/events/delete/<int:identity>', methods=['DELETE'])
def delete_event(identity):
    try:
        dt_id_query = f"SELECT [External_ID] FROM [dbo].vwDTOverview WHERE [ID] = {identity}"
        dt_id = db.sql_query(dt_id_query).squeeze()
    except Exception as e:
        return jsonify({"message": f"Failed to fetch External_ID: {str(e)}"}), 500

    try:
        if not dt_id:
            return jsonify({"message": "No event found for the provided identity"}), 404
    except Exception as e:
        return jsonify({"message": f"Failed to check if dt_id is empty: {str(e)}"}), 500

    try:
        deleted = db.delete_dt(identity=dt_id)
        if deleted:
            return jsonify({"message": "Event deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to delete event: {str(e)}"}), 500


@app.route('/events/search-in-events', methods=['GET'])
def search_data():
    site = request.args['site']
    turbine = request.args['turbine']
    category = request.args['category']
    # TODO contrôler que la catégorie existe
    id_result, comment_result = db.looking_for_in(site, turbine, category)

    id_result_serializable = int(id_result) if isinstance(id_result, (int, np.int64)) else id_result
    comment_result_serializable = str(comment_result) if isinstance(comment_result,
                                                                    (int, np.int64)) else comment_result

    response_data = {"ID": id_result_serializable, "Comment": comment_result_serializable}
    return jsonify(response_data), 200


@app.route('/events/set-exportation/<int:identity>', methods=['PUT'])
def set_exportation_endpoint(identity):
    input_datetime = datetime.utcnow()
    state = input_datetime.strftime('%Y-%m-%d %H:%M:%S')

    success = db.set_exportation(state, identity)

    if success:
        return jsonify({"message": f"Exportation state for ID {identity} updated successfully"}), 200
    else:
        return jsonify({"message": f"Failed to update exportation state for ID {identity}"}), 500


@app.route('/events/close/<int:identity>', methods=['PUT'])
def close_event(identity):
    close = request.headers.get('close')
    comment = request.headers.get('comment')

    # if close is None:
    #     return jsonify({"message": "State is missing in request headers"}), 400

    date_format = '%Y-%m-%d %H:%M'

    try:
        close_datetime = datetime.strptime(close, date_format)
    except ValueError:
       return jsonify({"message": "Invalid date format. Use %Y-%m-%d %H:%M"}), 400
    close_formatted = close_datetime.strftime(date_format)

    current_datetime = datetime.now()

    if close_datetime > current_datetime:
        return jsonify({"message": "Invalid date. Date cannot be in the future"}), 400

    # try:
    #     if not isinstance(comment, str) or not re.match("^[A-Za-z]+$", comment):
    #         raise ValueError("Invalid comment format.")
    # except ValueError as e:
    #     return jsonify({"message": f"{str(e)} Only text characters, dot, ^, and question mark are allowed."}), 400

    success = db.closing_event(close_formatted, identity, comment)

    if success:
        return jsonify({"message": f"Event {identity} closed successfully"}), 200
    else:
        return jsonify({"message": f"Failed to close event {identity}"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=80511)
