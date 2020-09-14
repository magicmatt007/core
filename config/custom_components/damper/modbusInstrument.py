# Source: https://minimalmodbus.readthedocs.io/en/stable/usage.html#general-on-modbus-protocol
# Dependencies:
#   pip install minimalmodbus
#   pip install pyserial

from datetime import date
import time

import minimalmodbus  # as mmRtu
import serial


class ModbusInstrument:
    instrumentCount = 0

    # Adjust modbus parameters to match configuration:
    port = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0" #"usb-1a86_USB2.0-Serial-if00-port0" #-> ../../ttyUSB0  RaspberryP
    # port = "com5"  # Windows10 left port on laptop
    # port = "com10"  # "com6" # Windows10 docking station
    # port = "com4"  # Windows10 HP right port on laptop
    baudrate = 19200 # 9600
    bytesize = 8
    parity = serial.PARITY_NONE
    # parity = serial.PARITY_EVEN # 9.6.2020: Changed from EVEN to NONE, as this is how what the script in server assigns. Surprisingly, only a new out of the box GDB revealed this bug, and existing GMAs didn't have a problem...
    stopbits = 1
    timeout = 1  # 0.2
    mode = minimalmodbus.MODE_RTU
    clear_buffers_before_each_transaction = True

    def __init__(self, slaveAddress):
        self.instrument = minimalmodbus.Instrument(ModbusInstrument.port, slaveAddress)  # port name, slave address (in decimal)

        # if ModbusInstrument.instrumentCount == 0: # Configure Modbus bus parameters, if this is the first device. 
        if True: # Configure Modbus bus parameters, if this is the first device. 
            ModbusInstrument.instrumentCount +=1
            #instrument.serial.port                    # this is the serial port name
            self.instrument.serial.baudrate = ModbusInstrument.baudrate      # Baud
            self.instrument.serial.bytesize = ModbusInstrument.bytesize
            self.instrument.serial.parity   = ModbusInstrument.parity
            self.instrument.serial.stopbits = ModbusInstrument.stopbits
            self.instrument.serial.timeout  = ModbusInstrument.timeout       # 0.05          # seconds
            self.instrument.mode = ModbusInstrument.mode                     # rtu or ascii mode
            self.instrument.clear_buffers_before_each_transaction = ModbusInstrument.clear_buffers_before_each_transaction
            self.instrument.address = slaveAddress                    # this is the slave address number

        # Siemens Registers (excerpt):
        # Reg      Name              RW    Unit  Scaling     Range/enumeration
        # 1        Setpoint          RW    %     0.01        0..100   
        # 2        Override control  RW    -     --          0 = Off / 1 = Open / 2 = Close / 3 = Stop / 4 = GoToMin / 5 = GoToMax
        # 3        Actual position   R     %     0.01        0..100
        # 256      Command           RW    --                0 = Ready / 1 = Adaption / 2 = Selftest / 3 = ReInitDevice / 4 = RemoteFactory / Reset
        # 1281     Factory Index     R
        # 1282-83  Factory Date      R


    def setpoint(self,value):  # 0 = closed; 10000 = open
        register = 1
        registerAddress = register - 1
        self.instrument.write_register(registerAddress, value, 0)  # !!Registernumber!!, value, number of decimals for storage
        #print(value)
        #print(self.instrument.read_register(registerAddress, 0))

    def overrideControl(self,value):
        register = 2
        registerAddress = register - 1
        self.instrument.write_register(registerAddress, value, 0)  # Registernumber, value, number of decimals for storage
        #print(value)
        #print(self.instrument.read_register(registerAddress, 0))

    def actualPosition(self):
        register = 3
        registerAddress = register - 1
        value = self.instrument.read_register(registerAddress, 0)
        #print(value)
        return value

    def factoryDate(self):
        register = 1282
        registerAddress = register - 1
        value1 = self.instrument.read_register(registerAddress, 0)
        register = 1283
        registerAddress = register - 1
        value2 = self.instrument.read_register(registerAddress, 0)
        byte1 = value2 % 0x100  # modulo = remains  = lower byte
        byte2 = value2 // 0x100 # divide with full integer  #divmod(value1, 0x100) = higher byte
        print([value1,value2])
        print(byte1, byte2)
        year = 2000+ value1
        month = byte2
        day = byte1
        # month = int(str(value2)[0:2]) #left(value2,2)
        # day = int(str(value2)[2:5]) #right(value2,2)
        print(year, month, day)

        return date(year,month,day)
        # return [value1,value2, year, month, day, date(year,month,day)]

    def factorySeqNum(self):
        register = 1284
        registerAddress = register - 1
        value1 = self.instrument.read_register(registerAddress, 0)
        register = 1285
        registerAddress = register - 1
        value2 = self.instrument.read_register(registerAddress, 0)
      
        # return f"{value1:04x}"+f"{value2:04x}"
        return value1 * 0x10000 + value2

    def factoryIndex(self):
        register = 1281
        registerAddress = register - 1
        value1 = self.instrument.read_register(registerAddress, 0)
        byte1 = value1 % 0x100  # modulo = remains  = lower byte
        byte2 = value1 // 0x100 # divide with full integer  #divmod(value1, 0x100) = higher byte
        return chr(byte2)
        # return value1
        # return f"{value1:04x}"
        
    def typeASN(self):
        value = []
        registerStart = 1409
        registerEnd = 1416

        for register in range(registerStart,registerEnd+1):
            registerAddress = register - 1
            value_reg = self.instrument.read_register(registerAddress, 0)
            value.append(value_reg)

        valueStr = ""
        for i in value:
            for j in i.to_bytes(2,'big'):
                if j!=0:
                    valueStr += chr(j)

        return(valueStr)    

    # Enhancement functions:
    def monitorPositionChange(self):
        
        runtime_max = 90
        interval = 0.5
        startTime = time.time()
        current = -10
        counter = 0
        time.sleep(2)
        for i in range(0,int(runtime_max / interval)):
            previous = current
            current = self.actualPosition()
            if current == previous:
                counter += 1
                print("break counter" + str(counter))
                if counter > 5:
                    print("break really")
                    break
            else:
                counter = 0
            print(f"{self.instrument.address}: Current ! position: {current}, ({(current/10000*90):.1f}°)")
            i=+1
            time.sleep(interval)
        print(f"Runtime: {(time.time() - startTime):.1f}s")