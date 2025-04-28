from rest_framework.views import APIView
from rest_framework.response import Response
import time
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from app.constants import app_constants as CONSTANTS
from app.defined_api.gru_algorithm import GatedRecurrentUnit
import serial
from app.models import Prediction, Cardiologist, Patient
from app.helpers.serializer_helpers import SerializerHelpers
import json
from django.contrib.auth.models import User

class Ports(APIView):

    def __init__(self):

        self.CONSTANT_MS_FROM_ARDUINO = 1000 / 10
        self.SIGNAL_SECONDS = CONSTANTS.SECONDS
        self.PREDICTION_ID = None

    def patch(self, request):
        """ Executes when PATCH is triggered. """
        
        rates = request.data['rates']
        prediction_id = request.data['prediction_id']
        
        GRU = GatedRecurrentUnit()
        prediction = GRU.predict_input_data(
            rates
        )

        Prediction.objects.all().filter(id = prediction_id).update(
            remarks = prediction
        )

        return Response(
            {
                "message": "Analyzed ECG data is " + str(prediction),
                "remarks": str(prediction)
            }, 200

        )

    def get(self, request):
        """ Executes when GET request is trigerred. """

        serial_ports = self.list_serial_ports()

        return Response({
            'message': 'Retrieved available ports.',
            'available_ports': serial_ports
        }, 200)
    
    def validate_post(self, request):

        serializer_instance = SerializerHelpers().create_serializer_no_depth(
            'Prediction', 'app'
        )
        serializer = serializer_instance(data=request.data)
        return serializer.is_valid()
    
    def insert_prediction(self, request):

        try:

            patient = request.data.get('patient', None)
            sequential_ecg = request.data.get('sequential_ecg', { "rates": [] })
            sequential_ecg = json.dumps(sequential_ecg)
            
            pred = Prediction.objects.create(

                attending_physician = Cardiologist.objects.get(
                    user = User.objects.get(username = request.user)
                ),

                patient = Patient.objects.get(id = patient),
                sequential_ecg = sequential_ecg,
                remarks = 'No Remark'
            )

            self.PREDICTION_ID = pred.pk

            return True
        except Exception as e:
            print(e)
            return False
        

    def post(self, request):
        """ Executes when POST request is trigerred. """

        self.PREDICTION_ID = None
        port = request.data.get('port', None)

        # print(port, "IS THE PORT")
        # input('test pause')
        if port is None:
            return Response({
                'message': 'No port provided.'
            }, 400)
        
        heart_rates = self.read_serial(port=str(port))
        if len(heart_rates) < 1:

            return Response({

                'message': 'Sensor is not working.'

            }, 400)

        # import pdb
        # pdb.set_trace()
        request.data['sequential_ecg'] = { "rates": heart_rates }
  
        if self.insert_prediction(request):

            return Response({
                'message': 'Record was created.',
                'prediction_id': self.PREDICTION_ID,
                'seconds': int((self.CONSTANT_MS_FROM_ARDUINO * self.SIGNAL_SECONDS) / 100) ,
                'rates': heart_rates

            }, 200)
    


    def list_serial_ports(self):
        """ List serial port(s) available. """

        if sys.platform.startswith('win'):
            ports = [f'COM{i}' for i in range(1, 256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = [f'/dev/ttyUSB{i}' for i in range(0, 10)]
        elif sys.platform.startswith('darwin'):
            ports = [f'/dev/tty.usbserial-{i}' for i in range(0, 10)]
        else:
            raise EnvironmentError("Unsupported platform")
        
        available_ports = [port for port in ports if os.path.exists(port)]
        return available_ports

    def read_serial(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        rates = []
        try:

            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                print(f"Connected to {port}")
                time.sleep(2)  # Allow time for the connection to establish

                while True:
                    if len(rates) > (self.CONSTANT_MS_FROM_ARDUINO * self.SIGNAL_SECONDS) - 1:
                        return rates
                    
                    data = ser.readline().decode().strip()

                    if data:
                        print("Reading ECG Signal(s) - Analog Rate", data)
                        rates.append(data)
                        
        except Exception as e:
            empty_list = []
            for i in range(0, 3000):
                empty_list.append(0)
            return empty_list
        return rates
