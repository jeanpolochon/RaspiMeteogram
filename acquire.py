import smbus
import time
import ConfigParser
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

# Define adresses of the sensors
HTS221 = 0x5F
LPS25H = 0x5D   #X-NUCLEO-IKS01A1
LPS22HB = 0x5D  #X-NUCLEO-IKS01A2 

####### Read temperature and humidity #######
def getTemperatureAndHumidity(bus, HTS221):
    # Wake up the device  (0x84 does not work)
    bus.write_byte_data(HTS221, 0x20, 0x85)

    # Humidity Calibration values
    H0 = bus.read_byte_data(HTS221, 0x30) / 2
    H1 = bus.read_byte_data(HTS221, 0x31) / 2

    val0 = bus.read_byte_data(HTS221, 0x36)
    val1 = bus.read_byte_data(HTS221, 0x37)
    H2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

    val0 = bus.read_byte_data(HTS221, 0x3A)
    val1 = bus.read_byte_data(HTS221, 0x3B)
    H3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

    # Temperature Calibration values
    T0 = bus.read_byte_data(HTS221, 0x32)
    T0 = (T0 & 0xFF)

    T1 = bus.read_byte_data(HTS221, 0x33)
    T1 = (T1 & 0xFF)

    raw = bus.read_byte_data(HTS221, 0x35)
    raw = (raw & 0x0F)

    # Convert the temperature Calibration values to 10-bits
    T0 = ((raw & 0x03) * 256) + T0
    T1 = ((raw & 0x0C) * 64) + T1

    val0 = bus.read_byte_data(HTS221, 0x3C)
    val1 = bus.read_byte_data(HTS221, 0x3D)
    T2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

    val0 = bus.read_byte_data(HTS221, 0x3E)
    val1 = bus.read_byte_data(HTS221, 0x3F)
    T3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)

    # Select control register2, 0x21
    #		0x01	One shot conversion
    # Useless with 0x85 in 0x20
    #bus.write_byte_data(HTS221, 0x21, 0x01)

    #While data is not ready, wait
    while ((bus.read_byte_data(HTS221, 0x27) & 0x03) != 3):
        time.sleep(0.1)

    # Read data back from 0x28 with command register 0x80, 4 bytes
    # humidity msb, humidity lsb, temp msb, temp lsb
    data = bus.read_i2c_block_data(HTS221, 0x28 | 0x80, 4)

    # Put the device back in sleep mode 
    bus.write_byte_data(HTS221, 0x20, 0x00)

    # Convert the data
    humidity = (data[1] * 256) + data[0]
    humidity = ((1.0 * H1) - (1.0 * H0)) * (1.0 * humidity - 1.0 * H2) / (1.0 * H3 - 1.0 * H2) + (1.0 * H0)
    temp = (data[3] * 256) + data[2]
    if temp > 32767 :
        temp -= 65536
    temperature = ((T1 - T0) / 8.0) * (temp - T2) / (T3 - T2) + (T0 / 8.0)

    print "Relative Humidity : %.1f %%" %humidity
    print "Temperature in Celsius : %.1f C" %temperature
    return temperature, humidity

####### Read pressure LPS22HB #######
def getPressure(bus, LPS22HB):
    # Wake up the device  (0x84 does not work)
    bus.write_byte_data(LPS22HB, 0x20, 0x95)
    
    # One shot measurement
    # Useless with 0x94 in 0x20
    #bus.write_byte_data(LPS22HB, 0x21, 0x01)

    while ((bus.read_byte_data(LPS22HB, 0x27) & 0x03) != 3):
        time.sleep(0.1)

    # Read data back from 0x28 with Command register, 0x80
    data = bus.read_i2c_block_data(LPS22HB, 0x28 | 0x80, 5)

    # Put the device back in sleep mode 
    bus.write_byte_data(LPS22HB, 0x20, 0x00)

    # Convert the data to hPa
    pressure = (data[2] * 65536 + data[1] * 256 + data[0]) / 4096.0

    # Convert the data to degrees. 
    temperature = data[4] * 256 + data[3]
    if (temperature & (1 << (16 - 1))) != 0: # if sign bit is set 
        temperature = temperature - (1 << 16)
    temperature = 42.5 + (temperature /480)

    print "Barometric Pressure is : %.1f hPa" %pressure
    print "Temperature is : %.1f C" %temperature

    return pressure

####### Write data on the DB #######
def writeToDB(temperature,humidity,pressure):
    _time=time.strftime('%Y-%m-%d %H:%M:%S')

    # Output data to screen
    print(_time)

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
        val = (_time,temperature,pressure,humidity)
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



def main():
    # Get I2C bus
    bus = smbus.SMBus(1)
    temperature, humidity = getTemperatureAndHumidity(bus, HTS221)
    pressure = getPressure(bus, LPS22HB)
    writeToDB(temperature,humidity,pressure)

main()