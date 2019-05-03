import smbus
import time
import ConfigParser
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

_time=time.strftime('%Y-%m-%d %H:%M:%S')

# Get I2C bus
bus = smbus.SMBus(1)

####### Read pressure #######
# Humidity Calibration values
# Read data back from 0x30, 1 byte
val = bus.read_byte_data(0x5F, 0x30)
H0 = val / 2

# Read data back from 0x31, 1 byte
val = bus.read_byte_data(0x5F, 0x31)
H1 = val /2

# Read data back from 0x36, 2 bytes
val0 = bus.read_byte_data(0x5F, 0x36)
val1 = bus.read_byte_data(0x5F, 0x37)
H2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

# Read data back from 0x3A, 2 bytes
val0 = bus.read_byte_data(0x5F, 0x3A)
val1 = bus.read_byte_data(0x5F, 0x3B)
H3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

# Temperature Calibration values
# Read data back from 0x32, 1 byte
T0 = bus.read_byte_data(0x5F, 0x32)
T0 = (T0 & 0xFF)

# Read data back from 0x32, 1 byte
T1 = bus.read_byte_data(0x5F, 0x33)
T1 = (T1 & 0xFF)

# Read data back from 0x35, 1 byte
raw = bus.read_byte_data(0x5F, 0x35)
raw = (raw & 0x0F)

# Convert the temperature Calibration values to 10-bits
T0 = ((raw & 0x03) * 256) + T0
T1 = ((raw & 0x0C) * 64) + T1

# Read data back from 0x3C, 2 bytes
val0 = bus.read_byte_data(0x5F, 0x3C)
val1 = bus.read_byte_data(0x5F, 0x3D)
T2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

# Read data back from 0x3E, 2 bytes
val0 = bus.read_byte_data(0x5F, 0x3E)
val1 = bus.read_byte_data(0x5F, 0x3F)
T3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)


# Select control register2, 0x21
#		0x01	One shot conversion
bus.write_byte_data(0x5F, 0x21, 0x01)

#While data is not ready, wait
while ((bus.read_byte_data(0x5F, 0x27) & 0x03) != 3):
	time.sleep(0.1)

# Read data back from 0x28 with command register 0x80, 4 bytes
# humidity msb, humidity lsb, temp msb, temp lsb
data = bus.read_i2c_block_data(0x5F, 0x28 | 0x80, 4)

# Convert the data
humidity = (data[1] * 256) + data[0]
humidity = ((1.0 * H1) - (1.0 * H0)) * (1.0 * humidity - 1.0 * H2) / (1.0 * H3 - 1.0 * H2) + (1.0 * H0)
temp = (data[3] * 256) + data[2]
if temp > 32767 :
	temp -= 65536
cTemp = ((T1 - T0) / 8.0) * (temp - T2) / (T3 - T2) + (T0 / 8.0)



####### Read pressure #######
# LPS25HB address, 0x5C
bus.write_byte_data(0x5D, 0x21, 0x01)

while ((bus.read_byte_data(0x5D, 0x27) & 0x03) != 3):
	time.sleep(0.1)

# Read data back from 0x28 with Command register, 0x80
# 3 bytes, Pressure LSB first
data = bus.read_i2c_block_data(0x5D, 0x28 | 0x80, 3)

# Convert the data to hPa
pressure = (data[2] * 65536 + data[1] * 256 + data[0]) / 4096.0

# Output data to screen
print(_time)
print "Relative Humidity : %.1f %%" %humidity
print "Temperature in Celsius : %.1f C" %cTemp
print "Barometric Pressure is : %.1f hPa" %pressure

config = ConfigParser.ConfigParser()
config.readfp(open(r'/home/pi/RaspiMeteogram/db.conf'))
_username = config.get('db-meteogram', 'username')
_password = config.get('db-meteogram', 'password')
_database = config.get('db-meteogram', 'database')
_table = config.get('db-meteogram', 'table')

try:
   connection = mysql.connector.connect(host='localhost',
                             database=_database,
                             user=_username,
                             password=_password)
   cursor = connection.cursor()
   sql = "INSERT INTO "+_table+"  (tdatetime, temperature, pressure, humidity) VALUES (%s, %s, %s, %s)"
   val = (_time,cTemp,pressure,humidity)
   result  = cursor.execute(sql, val)
   connection.commit()
   print ("Record inserted successfully into table")
except mysql.connector.Error as error :
    connection.rollback() #rollback if any exception occured
    print("Failed inserting record into table {}".format(error))
finally:
    #closing database connection.
    if(connection.is_connected()):
        cursor.close()
        connection.close()
