#!/usr/bin/env python
import datetime
import requests
import logging
# from sense_hat import SenseHat
from sense_emu import SenseHat

logging.getLogger().setLevel(logging.ERROR)
sense = SenseHat()
logging.getLogger().setLevel(logging.WARNING)
sense.clear()

print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),end=',')

raw_low=7.22
raw_hi=36.11
raw_range=raw_hi-raw_low

ref_low=47
ref_hi=80
ref_range=raw_hi-raw_low


#temperature_c = sense.get_temperature()
#temperature_f = ((9/5)*temperature_c)+32
#temperature_f = round(temperature_f)

reading=sense.get_temperature()
corrected_reading=(((reading - raw_low)*ref_range)/raw_range)+ref_low
temperature_f = round(corrected_reading)
print(f'Temp={temperature_f}', end=',')

pressure=sense.get_pressure()
pressure=round(pressure)
print(f'Pressure={pressure}', end=',')

humidity = sense.get_humidity()
humidity = round(humidity)
print(f'Humidity={humidity}', end=',')

#sense.show_message(f'Temp={temperature_f}')
#sense.show_message(f'Pressure={pressure}')
#sense.show_message(f'Humidity={humidity}')

where='http://maker.ifttt.com/trigger/temp_event/with/key/<insertKey>'
#where='https://johnfunk.com'
body={'value1':temperature_f,'value2':pressure,'value3':humidity}
#print(f'{where},{body}')
if (35 <=temperature_f <95) ==False:
	r=requests.post(url=where,json=body,timeout=5)
	print(f'{r}', end=',')
else:
	print('no alarm', end=',')
print(f'TempSensor={reading}')
