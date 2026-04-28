from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import re

app = Flask(__name__)


DATA_FILE = os.path.join('data', 'appointments.json')


os.makedirs('data', exist_ok=True)


if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def load_appointments():

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_appointments(appointments):

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(appointments, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/booking')
def booking():

    return render_template('booking.html')


@app.route('/api/appointments', methods=['POST'])
def create_appointment():

    try:
        data = request.get_json()

        required_fields = ['ownerName', 'phoneNumber', 'service', 'preferredDate']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400

        if not data.get('privacyConsent'):
            return jsonify({'error': 'Необходимо согласие с политикой конфиденциальности'}), 400


        phone_pattern = re.compile(r'^[\+\d\s\(\)\-]{7,}$')
        if not phone_pattern.match(data['phoneNumber']):
            return jsonify({'error': 'Некорректный номер телефона'}), 400


        appointments = load_appointments()


        new_appointment = {
            'id': len(appointments) + 1,
            'ownerName': data['ownerName'],
            'phoneNumber': data['phoneNumber'],
            'service': data['service'],
            'preferredDate': data['preferredDate'],
            'privacyConsent': data['privacyConsent'],
            'createdAt': datetime.now().isoformat(),
            'status': 'new'
        }

        appointments.append(new_appointment)
        save_appointments(appointments)

        return jsonify({
            'success': True,
            'message': 'Заявка успешно создана',
            'appointment': new_appointment
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/appointments', methods=['GET'])
def get_appointments():

    appointments = load_appointments()
    return jsonify(appointments)


if __name__ == '__main__':
    app.run(debug=True, port=5000)