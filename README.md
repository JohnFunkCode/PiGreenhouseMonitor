# PiGreenhouseMonitor
 Monitor Greenhouse with Raspberry Pi and Sense HAT

This is a simple Raspberry Pi project to monitor the temperature and humidity of a greenhouse. The data is logged to a 
file.  If the readings are above or below a reasonable threshold it sends an alert to my phone using IFTT.

## Deployment
This code is designed to run on a Raspberry Pi with a Sense HAT.  It is written in Python 3.  
It runs via a cron job every 5 minutes.  The cron job is set up as follows:
```
*/5 * * * * /home/pi/Documents/code/PiGreenhouseMonitor/print_sensor_data.py >> /home/pi/Documents/code/PiGreenhouseMonitor/temperature.txt
```