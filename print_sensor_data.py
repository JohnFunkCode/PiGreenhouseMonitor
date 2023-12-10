#!/usr/bin/env python
import os
import datetime

import requests
import logging
import yaml

# from sense_hat import SenseHat
from sense_emu import SenseHat


class greenhouseMonitorApp():
    def __init__(self):
        self.temperature_f = 0
        self.pressure = 0
        self.humidity = 0

        logging.getLogger().setLevel(logging.ERROR)
        self.sense = SenseHat()
        logging.getLogger().setLevel(logging.WARNING)
        self.sense.clear()

 
    def get_sensor_data(self):
        temp = self.sense.get_temperature()
        self.temperature_f = round(correct_sensor_data('Temperature', temp))
        self.temperature_f = self.sense.get_temperature()
        self.pressure = self.sense.get_pressure()
        self.humidity = self.sense.get_humidity()

    def report_sensor_data(self):
        body = {'value1': self.temperature_f, 'value2': self.pressure, 'value3': self.humidity}
        # print(f'{where},{body}')
        if (35 <= self.temperature_f < 95) == False:
            r=send_alert_to_iftt(body=body)
            print(f'{r}', end=',')
        else:
            print('no alarm', end=',')
        print(f'TempSensor={self.temperature_f}')


#######################################################################################
#  a few helper functions that I'll likely re-use in other raspberry pi sensor projects

def correct_sensor_data(sensor_name: str, reading) -> float:
    """adjusts the raw sensor reading using a two point calibration as described in the article
    at: https://learn.adafruit.com/calibrating-sensors/two-point-calibration using the named sensor
    parameters in config.yaml"""
    # RAW_LOW = 7.22
    # RAW_HI = 36.11
    # raw_range = RAW_HI - RAW_LOW
    #
    # REF_LOW = 47
    # REF_HI = 80
    # ref_range = RAW_HI - RAW_LOW
    with open('config.yaml') as f:
        config_data = yaml.load(f, Loader=yaml.FullLoader)
        RAW_LOW = config_data['Sensor-Calibration'][sensor_name]['raw_low']
        RAW_HI = config_data['Sensor-Calibration'][sensor_name]['raw_hi']
        raw_range = RAW_HI - RAW_LOW
        REF_LOW = config_data['Sensor-Calibration'][sensor_name]['ref_low']
        REF_HI = config_data['Sensor-Calibration'][sensor_name]['ref_hi']
        ref_range = REF_HI - REF_LOW

    corrected_reading = (((reading - RAW_LOW) * ref_range) / raw_range) + REF_LOW
    return corrected_reading

def send_alert_to_iftt( body:dict ) -> str:
    """Send the data in the dictionary to your webhook service using the webhook key specified in the .env file"""
    from dotenv import load_dotenv
    load_dotenv()
    iftt_webhook_key = os.getenv('IFTT_WEBHOOK_KEY')
    if not iftt_webhook_key:
        raise ValueError('Missing IFTT_WEBHOOK_KEY in .env file')

    iftt_webhook_url = f'http://maker.ifttt.com/trigger/temp_event/with/key/{iftt_webhook_key}'
    r = requests.post(url=iftt_webhook_url, json=body, timeout=5)
    return str(r)


if __name__ == "__main__":
    app = greenhouseMonitorApp()
    app.get_sensor_data()
    app.report_sensor_data()
