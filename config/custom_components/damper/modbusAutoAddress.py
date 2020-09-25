# Source: https://minimalmodbus.readthedocs.io/en/stable/usage.html#general-on-modbus-protocol
# Dependencies:
#   pip install minimalmodbus
#   pip install pyserial
import time

import minimalmodbus  # as mmRtu
import serial


def configureSlave(newSlaveAddress, newBaudrate, newTransmittionMode, newTermination):

    port = "/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0"  # "usb-1a86_USB2.0-Serial-if00-port0" #-> ../../ttyUSB0  RaspberryP
    # port = "com5"  # Windows10 left port on laptop
    # port = "com10"  # "com6" # Windows10 docking station# Windows10 docking station
    # port = "com4"  # Windows10 HP right port on laptop
    # port = "/dev/pts/1"  # Hassio Docker Development Container
    print(port)

    BusConfigCommand = 1  # 0 = Ready, 1 = Load
    newRegisters = [
        newSlaveAddress,
        newBaudrate,
        newTransmittionMode,
        newTransmittionMode,
        BusConfigCommand,
    ]

    #### Modbus master config to reach a device in auto configuration mode:   ####
    # Siemens values:
    baudrate = 19200  #  1-   9600
    bytesize = 8  #  8-
    parity = serial.PARITY_EVEN  #  E-
    stopbits = 1  #  1
    slaveAddress = 246
    # Further modbus master config:
    timeout = 0.2  # 0.2 in seconds
    mode = minimalmodbus.MODE_RTU
    clear_buffers_before_each_transaction = True
    #### end #####

    maxDuration = 20  # Maximum time in seconds, before giving up to configure
    interval = 0.3  # 0.3 Time in seconds between each connection attempt

    startTime = time.time()
    duration = 0
    attempts = 0
    instrument = None
    success = False
    while duration <= maxDuration:
        attempts += 1  # Count attempts
        duration = time.time() - startTime
        try:
            # Step 1: Try to connect to device:
            errorMessage = "Couldn't connect"
            instrument = minimalmodbus.Instrument(
                port, slaveAddress
            )  # port name, slave address (in decimal)  # close_port_after_each_call=False
            print(f"Attempt {attempts} T = {duration:.1f}s Conneceted!")
            errorMessage = "Couldn't write"  #

            # Configure MASTER (Not logical location to do it here, but used package minimalModbus is set-up this way):
            # instrument.debug = True
            instrument.serial.baudrate = baudrate  # Baud
            instrument.serial.bytesize = bytesize
            instrument.serial.parity = parity
            instrument.serial.stopbits = stopbits
            instrument.serial.timeout = timeout
            instrument.mode = mode
            instrument.clear_buffers_before_each_transaction = (
                clear_buffers_before_each_transaction
            )

            # Write new SLAVE configuration:
            instrument.write_registers(764 - 1, newRegisters)
            print(f"Attempt {attempts}: T = {duration:.1f} Wrote registers!")
            success = True
            break  # Exit loop, once successful
        except Exception as e:
            print(f"Attempt {attempts}: T = {duration:.1f}s {errorMessage} ({e})")

        time.sleep(interval)

    if success:
        print(f"Successful in {duration:.1f}s after {attempts} attempts")
        return True
    else:
        print("Timeout error")
        return False


#### Example how to use:

# #### Values for auto config:  ####
# newSlaveAddress = 5
# newBaudrate = 1 #9600
# newTransmittionMode = 2 # 2 = 1-8-N-1
# newTermination = 0 # 0 = off   1 = on
# #### end #####

# configureSlave(newSlaveAddress,newBaudrate,newTransmittionMode,newTermination)
