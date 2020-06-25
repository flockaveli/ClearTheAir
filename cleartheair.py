import time
import json
import board
import busio
import adafruit_bme280
import adafruit_ccs811
import serial
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
ccs = adafruit_ccs811.CCS811(i2c)

bme280.sea_level_pressure = 1013.25

ser = serial.Serial(
#   port='/dev/ttyAMA0',
   port='/dev/ttyS0',
   baudrate = 9600,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
)

# unique AWS hostname for this IoT device
HOST_NAME = "asgq5sqsfpjcc-ats.iot.us-east-1.amazonaws.com"
#relative path to the root AWS IoS CA file
ROOT_CA = "/home/pi/Downloads/root-CA.crt"
PRIVATE_KEY = "/home/pi/5973564fa2-private.pem.key"
CERT_FILE = "/home/pi/5973564fa2-certificate.pem.crt"

topic = "$aws/rules/readclear"


myMQTTClient = AWSIoTMQTTClient("CLEAR")
myMQTTClient.configureEndpoint(HOST_NAME, 8883)
myMQTTClient.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT_FILE)
myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)

myMQTTClient.connect()

loopCount = 0
while True:
    x = ser.readline()
    ppb = float((x[4])<<8 | (x[5]))
    payload = {}
    payload['boxname'] = "clear"
    payload['Temperature'] = bme280.temperature
    payload['Humidity'] = bme280.humidity
    payload['Pressure'] = bme280.pressure
    payload['Altitude'] = bme280.altitude
    payload['C02'] = ccs.eco2
    payload['TVOC'] = ccs.tvoc
    payload['Formaldehyde'] = ppb
    payload['timestamp'] = int(time.time())
    payloadJSON = json.dumps(payload)
    myMQTTClient.publish(topic, payloadJSON, 1)
    print('Published topic %s: %s\n' % (topic, payloadJSON))
    loopCount += 1
    time.sleep(10)


