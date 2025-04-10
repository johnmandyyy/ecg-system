import os
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from app.constants import app_constants as CONSTANTS
from app.models import JsonDataset
import requests
import json
import random
import math

class Arrhythmia:

    def __init__(self):
        """ Constructor for Arrythmia Dataset(s). """
        # self.initialize_datasets()
        # self.get_records()
        # self.iterate_value()
        # JsonDataset.objects.all().delete()
        # self.parse_json()
        # self.patterns()

    def patterns(self):
        # result = self.generate_healthy_pattern()
        # print(result, len(result))

        # JsonDataset.objects.all().filter(remarks = 'Normal').delete()

        # for i in range(0, 36):
        #     json_data = json.dumps({
        #         "rates": self.generate_healthy_pattern()
        #     })

        #     JsonDataset.objects.create(remarks = 'Normal', sequential_ecg = json_data)
        pass

    def generate_healthy_pattern(self):
        num_patterns = 10  # Number of sequences
        sequence_length = 3000  # Length of each sequence
        analog_min, analog_max = 1, 650  # Range of AD8232 values

        pattern = []
        base_value = random.randint(300, 350)  # Start in a typical mid-range value
        amplitude = random.randint(20, 50)  # Define a small amplitude for oscillations
        frequency = (2 * math.pi) / sequence_length  # Frequency for smooth cycles
        
        for i in range(sequence_length):
            sinusoidal_variation = amplitude * math.sin(frequency * i * 10)  # Oscillatory component
            noise = random.choice([-3, -2, -1, 0, 1, 2, 3])  # Small noise variations
            value = base_value + sinusoidal_variation + noise
            value = max(analog_min, min(analog_max, int(value)))  # Keep within range
            pattern.append(value)
        
        return pattern

    def parse_json(self):
        JsonDataset.objects.all().update(remarks = 'Arrhythmia')

    def initialize_datasets(self):
        """ Get dataset from MITBIH. """

        if os.path.isdir("mitdb"):
            print('You already have the data.')
        else:
            wfdb.dl_database('mitdb', 'mitdb')

    def get_records(self):
        """ A method to get record(s). """

        database = "mitdb"
        url = f"https://physionet.org/files/{database}/1.0.0/RECORDS"

        response = requests.get(url)
        if response.status_code == 200:
            record_list = response.text.split("\n")
        else:
            print("Error retrieving records")

        records = []
        for each in record_list:
            if each != '' and int(each) <= 215:
                records.append(each)
        return records
    
    def scale_value(self, values):
        """ A mapper value to adjust the dataset using the given sensor values. """

        old_min, old_max = min(values), max(values)  # Auto-detect min and max from input data
        new_min, new_max = CONSTANTS.MINIMUM_VALUE, CONSTANTS.MAXIMUM_VALUE  # Fixed target range

        # Apply scaling formula and convert to integer using round()
        return np.array([int(round(((v - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min)) for v in values])
    
    def convert_string_to_int(self, np_array):
        """ A method to convert string values to int. """

        converted_int_array = []
        for element in np_array:
            parsed_int = int(element)
            converted_int_array.append(parsed_int)
        
        return np.array(converted_int_array)
    
    def iterate_value(self):
        """ A method to check all record value(s) online. """

        record_list = self.get_records()
        
        # Sampling frequency (MIT-BIH dataset uses 360 Hz)
        fs = CONSTANTS.SAMPLING_FREQUENCY
        samples_to_load = CONSTANTS.SECONDS * fs  # 1 minute (60 seconds)

        # plt.figure(figsize=(12, 5))  # Adjusted figure size for one patient
        for i, record_name in enumerate(record_list):

            fsamp = f'mitdb/{record_name}'
            record = wfdb.rdsamp(fsamp, sampto=samples_to_load)
            signal = record[0][:, 0]  # First lead/channel
            scaled_values = self.scale_value(signal)
            scaled_values = self.convert_string_to_int(scaled_values)

        