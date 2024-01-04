#!/usr/bin/env python
import os
import datetime
from pathlib import Path
import requests
import logging
import yaml
import pandas as pd
from pandas import DataFrame
#import matplotlib.pyplot as plt


from sense_hat import SenseHat
# from sense_emu import SenseHat


class greenhouseMonitorApp():
    def __init__(self):
        self.reading_date = None
        self.reading_time = None
        self.inside_temperature_sensor = 0
        self.inside_temperature_f = 0
        self.inside_pressure = 0
        self.inside_humidity = 0

        self.outside_temperature_c = 0
        self.outside_temperature_f = 0
        self.outside_pressure = 0
        self.outside_humidity = 0

        self.outside_temperature_c_NWS = 0
        self.outside_temperature_f_NWS = 0
        self.outside_pressure_NWS = 0
        self.outside_humidity_NWS = 0

        self.outside_temperature_f_openweathermap = 0
        self.outside_pressure_openweathermap = 0
        self.outside_humidity_openweathermap = 0


        logging.getLogger().setLevel(logging.ERROR)
        self.sense = SenseHat()
        logging.getLogger().setLevel(logging.WARNING)
        self.sense.clear()

    def get_sensor_data(self):
        self.reading_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.reading_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.inside_temperature_sensor = self.sense.get_temperature()
        #self.inside_temperature_f = round(correct_sensor_data('Temperature', self.inside_temperature_sensor)) # linear correction
        self.inside_temperature_f = round((self.inside_temperature_sensor * 1.9) + 16.5)  # polynomial correction better matches themometers in the greenhouse
        self.inside_pressure = round(self.sense.get_pressure())
        self.inside_humidity = round(self.sense.get_humidity())

    def get_outside_data_from_nws(self):
        nws_station_id = ""
        with open('config.yaml') as f:
            config_data = yaml.load(f, Loader=yaml.FullLoader)
            nws_station_id = config_data['National-Weather-Service-Station']

        nws_station_url = f'https://api.weather.gov/stations/{nws_station_id}/observations/latest'
        r = requests.get(url=nws_station_url, timeout=5)
        if r.status_code == 200:
            data = r.json()

            self.outside_temperature_c_NWS = data['properties']['temperature']['value']
            if self.outside_temperature_c_NWS == None:
                self.outside_temperature_c_NWS = 0
            else:
                self.outside_temperature_f_NWS = self.outside_temperature_c * 1.8 + 32
            self.outside_pressure_NWS = data['properties']['barometricPressure']['value']
            if self.outside_pressure_NWS == None:
                self.outside_pressure_NWS = 0
            self.outside_humidity_NWS = data['properties']['relativeHumidity']['value']
            if self.outside_humidity_NWS == None:
                self.outside_humidity_NWS = 0
        else:
            print(f'Error getting data from {nws_station_url}')


    def get_outside_data_from_openweathermap(self):
        lat='39.799650'
        lon='-105.165640'

        from dotenv import load_dotenv
        load_dotenv()
        openweathermap_apikey = os.getenv('OPENWEATHERMAP_API_KEY')
        if not openweathermap_apikey:
            raise ValueError('Missing OPENWEATHERMAP_API_KE in .env file')

        openweathermap_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=imperial&appid={openweathermap_apikey}'
        r = requests.get(url=openweathermap_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            self.outside_temperature_f = round(data['main']['temp'])
            self.outside_pressure = round(data['main']['pressure'])
            self.outside_humidity = round(data['main']['humidity'])
        else:
            print(f'Error getting data from openweathermap.org')

    def record_readings_in_csv_file(self):
        readings_as_dict = {'Date': self.reading_date, 'Time': self.reading_time,
                    'Inside Temp Sensor': self.inside_temperature_sensor, 'Inside Temp': self.inside_temperature_f,
                    'Inside Humidity': self.inside_humidity,
                    'Outside Temp':self.outside_temperature_f, 'Outside Humidity': self.outside_humidity,
                    'Outside Temp NWS': self.outside_temperature_f_NWS}
        readings_as_df = DataFrame([readings_as_dict])

        path = Path('./GreenHouseReadings.csv')
        if path.is_file():
            #print("file exists append data to it")
            readings_as_df.to_csv('GreenHouseReadings.csv', index=False, mode='a', header=False)
        else:
            print("the .csv file does not exist create it")
            readings_as_df.to_csv('GreenHouseReadings.csv', index=False, mode='w', header=True)

    def log_readings(self):
        print(datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S'), end=',')
        print(
            f'InsideTemp={self.inside_temperature_f}, InsidePressure={self.inside_pressure}, InsideHumidity={self.inside_humidity} ',
            end=',')
        print(
            f'OutsideTemp={self.outside_temperature_f}, OutsidePressure={self.outside_pressure}, OutsideHumidity={self.outside_humidity}' ,
            end=',')
        print(
            f'OutsideTemp_NWS={self.outside_temperature_f_NWS}, OutsidePressure_NWS={self.outside_pressure_NWS}, OutsideHumidity_NWS={self.outside_humidity_NWS}' ,
            end=',')
        body = {'value1': f'in:{self.inside_temperature_f}', 'value2': f'out:{self.outside_temperature_f}'}
        if (9.33 <= self.inside_temperature_sensor < 35) == False:  # changed to alarming on the actual sensor reading rather than the adjusted values
            r = send_alert_to_iftt(body=body)
            print(f'{r}', end=',')
        else:
            print('no-alarm', end=',')
        print(f'InsideTempSensor={self.inside_temperature_sensor}')

    def graph_reading_history(self):
        df_to_graph = pd.read_csv('GreenHouseReadings.csv')
        # graph = df_to_graph.plot(x='Time', y=['Inside Temp', 'Outside Temp'], title='Greenhouse Temperature and Humidity', xlabel='Time', ylabel='Temperature (F)', xticks=df_to_graph.index, rot=90, figsize=(20,10), grid=True)
        graph = df_to_graph.plot(x='Time', y=['Inside Temp', 'Outside Temp'],
                                 title=f'Greenhouse Temperature {self.reading_date} {self.reading_time}', xlabel='Time', ylabel='Temperature (F)',
                                 figsize=(10, 5), grid=True, xticks=[])
        fig = graph.get_figure()
        fig.savefig('GreenHouseReadingsChart.png')

    def upload_graph_to_s3(self):
        import boto3
        s3 = boto3.resource('s3')
        s3.Bucket('johnfunk.com').upload_file(Filename='GreenHouseReadingsChart.png', Key='greenhouse/GreenHouseReadingsChart.png',
                                              ExtraArgs={'CacheControl': 'no-store,no-cache,private,max-age=60', 'ContentType': 'image/png'})
        # s3.Bucket('johnfunk.com').upload_file(Filename='index.html', Key='greenhouse/index.html',
        #                                       ExtraArgs={'CacheControl': 'no-store,no-cache,private,max-age=60', 'ContentType': 'text/html'})


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


def send_alert_to_iftt(body: dict) -> str:
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
    # app.get_outside_data_from_nws()
    app.get_outside_data_from_openweathermap()
    app.log_readings()
    app.record_readings_in_csv_file()
    app.graph_reading_history()
    app.upload_graph_to_s3()
