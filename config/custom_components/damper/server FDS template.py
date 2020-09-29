# coding=utf-8

### Imports from external libraries (=dependencies), which require manual install via pip install before use:
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from flask_socketio import SocketIO, join_room, emit, send

#from flask_jsonpify import jsonify

### Imports from standard Python libs:
# import json
from json import dumps, loads
from random import randint
import time
import asyncio
from datetime import date, datetime

### Imports from within this project:
from entities.entity import Session, engine, Base, func 
from entities.damper import Damper, DamperSchema 
from entities.group import Group, GroupSchema 
from entities.controller import Controller, ControllerSchema 
from entities.test import Test, TestSchema 
from entities.report import Report, ReportSchema 
from fireDAC import FireDAC
# from temp import Temp  ### temp code for debugging
# from control import createDampers
import modbusAutoAddress


# Modbus test:
from modbusInstrument import ModbusInstrument
instruments = []

# try:
#     instruments.append(ModbusInstrument(5))  # Create new instrument with address 5 and append it to the instruments array, that keeps all connected devices
# except:
#     print("Error (Create Instrument). Have you connected the Modbus interface?") 

# end Modbus init

# Creating the Flask application
app = Flask(__name__)
api = Api(app)
CORS(app)  # Needs to be made cybersecure before delivery to production
socketio = SocketIO(app, cors_allowed_origins="*") # Needs to be made cybersecure before delivery to production

# if needed, generate database schema
Base.metadata.create_all(engine)

# Vars from "Control" (FireDAC)
dampers = []
temp_timefactor = 10
runtime_open_max = 60 / temp_timefactor
runtime_close_max = 20 / temp_timefactor



# Socket API:
#######################################################
position = 1.0
# damper_is_testing_temp = False # Used temporarily, to allow cancellation of running damper test
dampers_currently_testing = [] # Used to allow avoid starting a damper test, when the damper is currently testing


@socketio.on('modbustest')   # 'modbustest' = eventname
def modbus_test(args):
    # damper_id = str(arg)
    # args = args.get_json()
    args = loads(args)
    damper_id = args['damper_id']
    report_id = args['report_id']
    print(f'Damper ID: {damper_id}, Report ID: {report_id}')

    modbus_address = int(getDamper(damper_id)["modbus_address"])
   
    print(f'damper_id from socket: {damper_id}')
    print("MODBUS test socket!")
    print(f'Modbus address: {modbus_address}')

    # data = {'position': -1,'state': 'closed', 'error': 'none', 'runtime_open': None, 'runtime_close': None, 'power': None, 'overall_indicator': 'TEST'}  # This is a dictionary
    data = {'position': -1,'state': 'closed', 'error': 'none', 'runtime_open': None, 'runtime_close': None, 'power': None, 
            'overall_indicator': 'TEST', 'runtime_close_indicator': 'TEST', 'runtime_open_indicator': 'TEST', 'power_indicator': 'TEST'}  # This is a dictionary
   

    runtime_max = 90
    interval = 1
    global error_count
    error_count = 0
    global position
    # global damper_is_testing_temp
    global dampers_currently_testing

    if modbus_address in dampers_currently_testing:
        print('Damper is already testing. Please wait' + str(dampers_currently_testing))
        return
    else:
        dampers_currently_testing.append(modbus_address)
        print('Damper is not yet testing. Starting now' + str(dampers_currently_testing))

    ######### Close:
    try:
        instrument = ModbusInstrument(modbus_address)  # 
        instrument.setpoint(0)
        data["state"] = "Closing"

        startTime = time.time()
        current = -10
        counter = 0
        # socketio.sleep(3)

        for i in range(0,int(runtime_max / interval)):
          previous = current

          try: 
              current = instrument.actualPosition()
          except Exception as e:
              error_count += 1
              print(f"Error count {error_count}. Error (Damper test, close, act position). OPEN. Have you connected the Modbus interface?" + str(e))
              data["error"] = 'Close error, act pos' + str(e)
              # damper_is_testing_temp = False 
            #   dampers_currently_testing.remove(modbus_address)
            #   if True: #error_count >=3:
            #       raise NameError('HiThere Close')

          print( f"{modbus_address} - Current: {current}, Previous: {previous}")
          if current == previous: # TO DO: Replace this clumsy end position detection with a better one                       
            counter = counter + 1
            print("break counter" + str(counter))
            if counter > 2:
              print("break realy")
              counter = 0
              break
          else:
            print("reset counter to 0")
            counter = 0
          print(f"{modbus_address} - Current position: {current}, ({(current/10000*90):.1f}°)")
          position = round(current/10000*90,0)
          data["position"] = position
          emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
          socketio.sleep(interval)

        data["state"] = "Closed"  
        data["runtime_close"] = round((time.time() - startTime),1)
        print(f"Runtime: {(data.get('runtime_close')):.1f}s")
        print(data.get("runtime_close"))
        emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
        
    except Exception as e:
        error_count += 1
        print(f"Error count {error_count}. Error (Damper test). Have you connected the Modbus interface?" + str(e))
        # damper_is_testing_temp = False 
        if True:  # error_count >=3:
            dampers_currently_testing.remove(modbus_address)
            data["error"] = 'Close error: ' + str(e)
            emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
            return


    socketio.sleep(5) # TO DO: Remove this sleep in open position after debugging

    ######### Open:
    try:
        instrument = ModbusInstrument(modbus_address)  # 
        instrument.setpoint(3000)  # 3000
        data["state"] = "Opening"

        # global position

        startTime = time.time()
        current = -10
        time.sleep(3)
        # global counter
        counter = 0

        for i in range(0,int(runtime_max / interval)):
          previous = current
          try: 
              current = instrument.actualPosition()
          except Exception as e:
              error_count += 1
              print(f"Error count {error_count}. Error (Damper test). OPEN. Have you connected the Modbus interface?" + str(e))
              data["error"] = 'Open error, act pos' + str(e)
              # damper_is_testing_temp = False 
            #   dampers_currently_testing.remove(modbus_address)
            #   if True:  # error_count >=3:
            #       raise NameError('HiThere Open')

        
          print( f"Current: {current}, Previous: {previous}")
          if current == previous:    # TO DO: Replace this clumsy end position detection with a better one
            counter = counter + 1
            print("break counter" + str(counter))
            if counter > 2:
              print("break realy")
              counter = 0
              break
          else:
            print("reset counter to 0")
            counter = 0
          print(f"Current position: {current}, ({(current/10000*90):.1f}°)")
          
          position = round(current/10000*90,0)

          data["position"] = position
          emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON

          socketio.sleep(interval)
        data["state"] = "Open"  
        data["runtime_open"] = round((time.time() - startTime),1)
        data["power"] = randint(15,35)/10
        print(f"Runtime: {(data.get('runtime_open')):.1f}s")
        print(data.get("runtime_open"))
        emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
        
    except Exception as e:
        error_count += 1
        print(f"Error count {error_count}. Error (Damper test). Have you connected the Modbus interface?" + str(e))
        # damper_is_testing_temp = False 
        if True: # error_count >=3:
            dampers_currently_testing.remove(modbus_address)    
            data["error"] = 'Init error: ' + str(e)
            emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
            return
    dampers_currently_testing.remove(modbus_address)  # physical test is finshed -> allow new tests

    #### WIP: Derive device performance indicators from test results ######
    #

    # runtime_open = 38.0 * 0.89
    # runtime_close = 38.0 * 0.89
    # power = 3.0 * 0.89

    runtime_open = data["runtime_open"]
    runtime_close = data["runtime_close"]
    power = data["power"]

    # TO DO: Replace this static values with user defined values from database:
    runtime_open_max = 42.0
    runtime_close_max = 42.0
    power_max = 3.0
    ######################

    # TO DO: Move import statement and class definition outside of this function: (I'm surprised that it works here :-))
    from enum import Enum
    class Indicator(Enum):
        PASS= 1
        WARNING = 2
        FAILURE = 3

    ratio = runtime_close / runtime_close_max
    if ratio > 1:
        indicator = Indicator.FAILURE
    elif ratio >= 0.9:
        indicator = Indicator.WARNING
    else:
        indicator = Indicator.PASS
    runtime_close_indicator = indicator

    ratio = runtime_open / runtime_open_max
    if ratio > 1:
        indicator = Indicator.FAILURE
    elif ratio >= 0.9:
        indicator = Indicator.WARNING
    else:
        indicator = Indicator.PASS
    runtime_open_indicator = indicator

    ratio = power / power_max
    if ratio > 1:
        indicator = Indicator.FAILURE
    elif ratio >= 0.9:
        indicator = Indicator.WARNING
    else:
        indicator = Indicator.PASS
    power_indicator = indicator

    overall_indicator = Indicator(max(runtime_close_indicator.value, runtime_open_indicator.value, power_indicator.value))
    print(runtime_close_indicator.name, runtime_open_indicator.name, power_indicator.name, overall_indicator.name)

    data["overall_indicator"] = overall_indicator.name

    emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON

    #
    ####################

    
    # Add test results to database:
    test_results = {'runtime_open': data["runtime_open"], 'runtime_close': data["runtime_close"], 
                    'power': data["power"], 'tested_at': str(datetime.now()), 'damper_id': damper_id, 'report_id': report_id,
                    'runtime_open_indicator': runtime_open_indicator.name, 'runtime_close_indicator': runtime_close_indicator.name,
                    'power_indicator': power_indicator.name,'overall_indicator': overall_indicator.name}
    print(test_results)

    args = test_results
    schema = TestSchema().load(args)  # Load = Deserialize a data structure to an object defined by this Schema’s fields. Returns a dict of deserialized data
    py_object = Test(**schema) # The ** notation is "unpacking" the dictionary into keyword argument for the function call
    
    Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
    session = Session() # start session

####### WIP 

    # def put(self, record_id): # PUT method = Update item via SQL update
    #     print("Controler PUT called: "+ str(record_id))
    #     args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
    #     schema = ControllerSchema().load(args) # Deserialize data structure to an object defined by this Schema’s fields types and formats, e.g. convert str "dates" to datetime
    #     schema["updated_at"] = datetime.now() # update timestamp to current date & time

    #     Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
    #     session = Session() # start session
    #     session.query(Controller).filter_by(id=record_id).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update
    #     session.commit() # Write to database
    #     session.close() # Close session
    
    #     return record_id 

#####
    print("damper_id: " + str(damper_id) + ", report_id: " + str(report_id) )
    # x = session.query(Test).filter_by(damper_id=damper_id, report_id=report_id).first()   #.update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update

    # How many tests exist with the damper_id and report_id already?:
    y = session.query(Test).filter_by(damper_id=damper_id, report_id=report_id).count()
    print("y: " + str(y))

    if y == 0:    # If none exists, add a new one
        print("Added new test report")
        # Add a new test to the database, if there is non with this report id and damper id:
        session.add(py_object) # The add function gets the table name from the object.
    
    else: # Otherwise update the latest one:
        print("Updated existing test report")
        # # Implementation Option 1: Get the maximum Test.id as an integer value:
        # subqry = session.query(func.max(Test.id)).filter_by(damper_id=damper_id,report_id=report_id)
        # t = subqry.scalar()
        # session.query(Test).filter_by(damper_id=damper_id,report_id=report_id, id = t).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update

        # Implementation Option 2: Get the maximum Test.id as a subquery, and include this subquery in the update query. Note: Requires syncrhonize_session=False: 
        subqry2 = session.query(func.max(Test.id)).filter_by(damper_id=damper_id,report_id=report_id).subquery()
        session.query(Test).filter(Test.damper_id == damper_id, Test.report_id == report_id, Test.id == subqry2).update(schema, synchronize_session=False) # Update record via SQL Expression, as there is no ORM equivalent for update

    session.commit() # Write to database
    new_id = py_object.id  # This is the auto generated new (or existing) primary key ID of the just added record
    session.close()

    return new_id 




###### These funtions were used for socket PoCs only. Delete after debugging:
#############################################################################
#

@socketio.on('startcounter')
def start_counter():
    print("start_counter")
    global position
    for i in range(0,100):
        socketio.sleep(0.5) 
        position = i
        get_data()

@socketio.on('getdata')
def get_data():
    global position
    print("get_data (broadcast): " + str(position))
    emit('data', str(position),broadcast = True)
#
#############################################################################

#### This funcation was used for PoC. Either implement in front end, or delete after debugging:
#####################################################################################################
#
#


@socketio.on('modbuslifedatatemp')
def modbus_life_data_temp():

    modbus_address = 55  #  TO DO: make variable again e.g. via  int(getDamper(damper_id)["modbus_address"])
    runtime_max = 90
    interval = 1
    
    print("MODBUS Open socket!")
    print(f'Modbus address: {modbus_address}')
    
    try:
      instrument = ModbusInstrument(modbus_address)  # 
      instrument.setpoint(3000)

      global position

      startTime = time.time()
      current = -10
      time.sleep(3)
      # global counter 
      counter = 0
      for i in range(0,int(runtime_max / interval)):
        previous = current
        current = instrument.actualPosition()
        print( f"Current: {current}, Previous: {previous}")
        if current == previous:
          counter = counter + 1
          print("break counter" + str(counter))
          if counter > 2:
            print("break really")
            counter = 0
            break
        else:
          print("reset counter to 0")
          counter = 0
        print(f"Current position: {current}, ({(current/10000*90):.1f}°)")
        
        position = round(current/10000*90,0)
        get_data()
        socketio.sleep(interval)
      print(f"Runtime: {(time.time() - startTime):.1f}s")

    except Exception as e:
        print("Error (Damper open). Have you connected the Modbus interface?" + str(e)) 


@socketio.on('modbuslifedataclosetemp')
def modbus_life_data_close_temp():

    modbus_address = 55  #  TO DO: make variable again e.g. via  int(getDamper(damper_id)["modbus_address"])
    runtime_max = 90
    interval = 1

    print("MODBUS Close socket!")
    print(f'Modbus address: {modbus_address}')
    try:
        instrument = ModbusInstrument(modbus_address)  # 
        instrument.setpoint(0)

        global position

        startTime = time.time()
        current = -10
        time.sleep(3)
        # global counter
        counter = 0
        index = 0        

        for i in range(0,int(runtime_max / interval)):
          previous = current
          current = instrument.actualPosition()
          print( f"Current: {current}, Previous: {previous}")
          if current == previous:
            counter = counter + 1
            print("break counter" + str(counter))
            if counter > 2:
              print("break really")
              counter = 0
              break
          else:
            print("reset counter to 0")
            counter = 0
          print(f"Current position: {current}, ({(current/10000*90):.1f}°)")
          
          position = round(current/10000*90,0)
          get_data()
          socketio.sleep(interval)
        print(f"Runtime: {(time.time() - startTime):.1f}s")

    except Exception as e:
        print("Error (Damper open). Have you connected the Modbus interface?" + str(e)) 
#
#
#############################################################################


# HTTP REST like API to sql database:
#######################################################

def getDamper(damper_id): # This helper method is used several times for REST and SOCKET to get Modbus address associated with a damper id
    Base.metadata.create_all(engine)
    session = Session() # start session
    damper_objects = session.query(Damper).get(damper_id)  
    session.close()

    # transforming into JSON-serializable objects
    schema = DamperSchema(many=False)
    dampers = schema.dump(damper_objects)
    # Debug to backend:
    print('### getDamper:')
    print(dampers,)

    return dampers

@app.route("/")
def hello():
    return jsonify({'text':'Hello World! Flask routing works!'})

# api.add_resource(GetGroup, '/getgroup/<int:group_id>') # returns one "Group" object
@app.route("/modbuscmdopen/<int:damper_id>")
def modbusOpen(damper_id):
    modbus_address = int(getDamper(damper_id)["modbus_address"])

    print("MODBUS Open!")
    print(f'Modbus address: {modbus_address}')
    try:
        instrument = ModbusInstrument(modbus_address)  # 
        instrument.setpoint(3000)
        instrument.monitorPositionChange()
        return jsonify({'Server feedback':'Received Damper Open Command'})
    except Exception as e:
        print("Error (Damper open). Have you connected the Modbus interface?" + str(e)) 
        return jsonify({'Server feedback':'Error (Damper open). Have you connected the Modbus interface?'})

@app.route("/modbuscmdclose/<int:damper_id>")
def modbusClose(damper_id):
    modbus_address = int(getDamper(damper_id)["modbus_address"])
    print("MODBUS Close!")
    print(f'Modbus address: {modbus_address}')
    try:
        instrument = ModbusInstrument(modbus_address)
        instrument.setpoint(00000)
        instrument.monitorPositionChange()
        return jsonify({'Server feedback':'Received Damper Close Command'})
    except Exception as e:
        print("Error (Damper close). Have you connected the Modbus interface?" + str(e)) 
        return jsonify({'Server feedback':'Error (Damper close). Have you connected the Modbus interface?'})


@app.route("/modbuscmdcls")
def modbusClose2():
    print("MODBUS Close!")
    try:
        instruments[0].setpoint(00000)
        instruments[0].monitorPositionChange()
        return jsonify({'Server feedback':'Received Damper Close Command'})
    except:
        print("Error (Damper Close). Have you connected the Modbus interface?") 
        return jsonify({'Server feedback':'Error (Damper Close). Have you connected the Modbus interface?'})


@app.route("/modbusassignaddr", methods=["POST"])
def modbusAssignAddr(nextAddress = 0):    # Optional argument allows calling this method from Python instead of REST
    restCall: bool  # required to have slightly different method behaviour on REST calls vs Pyhton calls
    if nextAddress == 0: # If called via REST then get nextAddress from its payload:
        restCall = True
        args = request.get_json()
        nextAddress = args['nextAddress']
        print(f"Received nextAddress via REST: {nextAddress}")
    else: 
        restCall = False
        print(f"Received nextAddress via Python call: {nextAddress}")
    # nextAddress = 5

    #### Values for push button config:  ####
    newSlaveAddress = nextAddress
    newBaudrate = 2 # 0 = auto / 1 = 9600 / 2 = 19200 3 = 38400 / 4 = 57600 / 5 = 76800  6 = 115200
    newTransmittionMode = 2 # 2 = 1-8-N-1
    newTermination = 0 # 0 = off   1 = on
    #### end #####

    try:
        success = modbusAutoAddress.configureSlave(newSlaveAddress,newBaudrate,newTransmittionMode,newTermination)
        time.sleep(3) # added temporarily for debugging GDB111.1E/MO
        instrument = ModbusInstrument(newSlaveAddress)
        type_asn = instrument.typeASN()
        manufacturing_date = instrument.factoryDate()
        factory_index = instrument.factoryIndex()
        factory_seq_num = instrument.factorySeqNum()
        if restCall == True:
            if success:
                addNewDamperToDb(newSlaveAddress,type_asn,manufacturing_date,factory_index,factory_seq_num)
            return jsonify(success)  # True or False; Note, as success is boolean, no quotes are used for the values true / false
        else:
            return success

    except Exception as e:
        print("Error (modbusAssignAddr). Have you connected the Modbus interface?" + str(e)) 
        if restCall == True:
            return jsonify(False)
        else:
            return False

def addNewDamperToDb(newSlaveAddress,type_asn,manufacturing_date,factory_index,factory_seq_num):
    Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
    session = Session() # start session

    # Create damper:    
    runtime_open = runtime_open_max + randint(-20,20) / temp_timefactor
    runtime_close = runtime_close_max + randint(-10,10) / temp_timefactor
    # create and persist dummy damper:
    python_damper = Damper(newSlaveAddress, runtime_open,runtime_close,type_asn,manufacturing_date,factory_index,factory_seq_num)  # (modbus_address,runtime_open_mock,runtime_close_mock)
    session.add(python_damper)
    session.commit()
    session.close()
    print("Created Damper!")    

class Commission(Resource):  # This currently generates virtual dampers in the database only, so these can be used in the front end.
    def get(self):
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        
        # Create dampers:
        totalDampers = 2  # randint(3,6)    
        for i in range (totalDampers):
            runtime_open = runtime_open_max + randint(-20,20) / temp_timefactor
            runtime_close = runtime_close_max + randint(-10,10) / temp_timefactor
            type_asn = "No ASN"
            manufacturing_date = date(2020,4,30)
            factory_index = "Z"
            factory_seq_num = 999999
            # create and persist dummy damper:
            python_damper = Damper(5, runtime_open,runtime_close,type_asn,manufacturing_date, factory_index, factory_seq_num)  # (modbus_address,runtime_open_mock,runtime_close_mock)
            session.add(python_damper)
        session.commit()
        session.close()
        print("Created "+str(totalDampers)+" Dampers:")    

        ##### Debug to console:
        # reload dampers
        damper_objects = session.query(Damper).all()
        session.close()
        # show existing dampers
        print('### Damper:')
        for damper in damper_objects:
            print(f'(UID: {damper.uid}), Name: {damper.name}')

        # transforming into JSON-serializable objects
        schema = DamperSchema(many=True)
        dampers = schema.dump(damper_objects)
        print(dampers)

        return jsonify(dampers)

class Dampers(Resource): # Provides all damper objects as an "array of JSONs"
    def get(self):
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Damper).order_by(Damper.id).all()  # Get all records 
        session.close() # Close session

        schema = DamperSchema(many=True)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got dampers:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

class CreateGroup(Resource):  # Generates a group and returns its ID
    def get(self):  # TO DO: Convert this from "GET" to "POST" (here in the backend and the front end)

        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session

        # Create group:
        python_group = Group("Test Group")  # (name)
        session.add(python_group)
        session.commit()
        new_id = python_group.id   
        session.close()
        print("Created one new group")
         
        ##### Debug to console: show all groups:
        group_objects = session.query(Group).all()
        session.close()
        print('### Groups:')
        for group in group_objects:
            print(f'(ID: {group.id}), Name: {group.name}')

        return new_id  
        

class Groups(Resource): # Provides all group objects as an "array of JSONs"
    def get(self):
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Group).order_by(Group.id).all()  # Get all record 
        session.close() # Close session

        schema = GroupSchema(many=True)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got groups:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON


class Tests(Resource): # Provides all test objects as an "array of JSONs"
    def get(self):
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Test).order_by(Test.id).all()  # Get all record 
        session.close() # Close session

        schema = TestSchema(many=True)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got tests:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

class Reports(Resource): # Provides all report objects as an "array of JSONs"
    def get(self):
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Report).order_by(Report.id).all()  # Get all record 
        session.close() # Close session

        schema = ReportSchema(many=True)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got reports:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON


class GetGroup(Resource): # Provides one group object as an JSON
    def get(self, record_id):
        print(f'Group ID: {record_id}')

        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Group).get(record_id)  # Get record 
        session.close() # Close session

        schema = GroupSchema(many=False)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got 1 group:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

class SaveGroup(Resource):  # WIP. Adds dampers to a group by assigning them the corresponding group ID:
    def post(self):
        print("SaveGroup POST called")
        args = request.get_json()
        group_id = args['group_id']
        group_name = args['group_name']
        selected_dampers = args['selected_dampers']
        print(f"Received group_id: {group_id}")
        print(f"Received group_name: {group_name}")
        print(f"Received selected_dampers: {selected_dampers}")

        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session

        if group_id == 0:  # group_id = 0 --> User requestd creation of a new group.
            # 1. Create group:
            # 1a: Generate a new group record first with any name.
            python_group = Group(group_name)  # Table "Group" (name)  ## Update: Use the received group name.
            session.add(python_group)
            session.commit()
            group_id = python_group.id   # = New group_id using auto assigned ID from database table
            # 1b: If the group_name was emtpy, then use its auto generate ID to generate a standard name:
            if group_name == "":
                print('Group name was empty')
                group_name = f'Group {group_id}' # = New group_name using auto assigned ID from database table and fix prefix
            print(f'Created new group with name {group_name}')
        else:
            print('Using existing group')

        print(f'new_id: {group_id}')
        print(f'new_name: {group_name}')
        
        x = session.query(Group).get(group_id)  # get(i) returns row with primary key i
        print(f'X.name: {x.name}')
        x.name = group_name
        session.commit()
         
        # 2. Remove all dampers from this group, which are not in the selectedDamper array:
        damper_object = session.query(Damper).all()
        for damper in damper_object:
            if damper.group_id == group_id:
                damper.group_id = None
        session.commit()

        # 3. Add the group_id to all selectedDampers:
        for i in selected_dampers:
            x = session.query(Damper).get(i)  # get(i) returns row with primary key i
            print(f"Damper ID: {x.id}, group ID: {x.group_id}")
            x.group_id = group_id
        session.commit()    

        ##### Debug to console: reload dampers:
        damper_objects = session.query(Damper).all()
        print('### Damper:')
        for damper in damper_objects:
            print(f'(ID: {damper.id}), Name: {damper.name}, Group-ID: {damper.group_id}')

        session.close() # close session
        return group_id


class ControllerREST(Resource):  #REST API for controllers: GET/POST/PUT/DELETE
    def get(self, record_id): # GET method = read existing item
        print(f'Controller GET called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Controller).get(record_id)  # Get record 
        session.close() # Close session

        schema = ControllerSchema(many=False)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got 1 controller:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

    def post(self, record_id):   # POST method = Create new item
        print("Controler POST called")
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = ControllerSchema().load(args)  # Load = Deserialize a data structure to an object defined by this Schema’s fields. Returns a dict of deserialized data
        py_object = Controller(**schema) # The ** notation is "unpacking" the dictionary into keyword argument for the function call
     
        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.add(py_object) # The add function gets the table name from the object.
        session.commit() # Write to database
        new_id = py_object.id  # This is the auto generated new primary key ID of the just added record
        session.close()

        return new_id 

    def put(self, record_id): # PUT method = Update item via SQL update
        print("Controler PUT called: "+ str(record_id))
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = ControllerSchema().load(args) # Deserialize data structure to an object defined by this Schema’s fields types and formats, e.g. convert str "dates" to datetime
        schema["updated_at"] = datetime.now() # update timestamp to current date & time

        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.query(Controller).filter_by(id=record_id).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update
        session.commit() # Write to database
        session.close() # Close session
    
        return record_id 

    def delete(self, record_id): # DELETE method = delete existing item
        print(f'Controller DELETE called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Controller).get(record_id)  # Get record 
        session.delete(db_object)  # Delete record
        session.commit() # Write to database
        session.close() # Close session

        return record_id

class TestREST(Resource):  #REST API for tests: GET/POST/PUT/DELETE
    def get(self, record_id): # GET method = read existing item
        print(f'Test GET called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Test).get(record_id)  # Get record 
        session.close() # Close session

        schema = TestSchema(many=False)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got 1 test:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

    def post(self, record_id):   # POST method = Create new item
        print("Controler POST called")
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = TestSchema().load(args)  # Load = Deserialize a data structure to an object defined by this Schema’s fields. Returns a dict of deserialized data
        py_object = Test(**schema) # The ** notation is "unpacking" the dictionary into keyword argument for the function call
     
        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.add(py_object) # The add function gets the table name from the object.
        session.commit() # Write to database
        new_id = py_object.id  # This is the auto generated new primary key ID of the just added record
        session.close()

        return new_id 

    def put(self, record_id): # PUT method = Update item via SQL update
        print("Controler PUT called: "+ str(record_id))
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = TestSchema().load(args) # Deserialize data structure to an object defined by this Schema’s fields types and formats, e.g. convert str "dates" to datetime
        schema["updated_at"] = datetime.now() # update timestamp to current date & time

        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.query(Test).filter_by(id=record_id).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update
        session.commit() # Write to database
        session.close() # Close session
    
        return record_id 

    def delete(self, record_id): # DELETE method = delete existing item
        print(f'Test DELETE called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Test).get(record_id)  # Get record 
        session.delete(db_object)  # Delete record
        session.commit() # Write to database
        session.close() # Close session

        return record_id

class DamperREST(Resource):  #REST API for dampers: GET/POST/PUT/DELETE
    def get(self, record_id): # GET method = read existing item
        print(f'Damper GET called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Damper).get(record_id)  # Get record 
        session.close() # Close session

        schema = DamperSchema(many=False)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got 1 damper:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

    def post(self, record_id):   # POST method = Create new item
        print("Damper POST called")
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = DamperSchema().load(args)  # Load = Deserialize a data structure to an object defined by this Schema’s fields. Returns a dict of deserialized data
        py_object = Damper(**schema) # The ** notation is "unpacking" the dictionary into keyword argument for the function call
     
        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.add(py_object) # The add function gets the table name from the object.
        session.commit() # Write to database
        new_id = py_object.id  # This is the auto generated new primary key ID of the just added record
        session.close()

        return new_id 

    def put(self, record_id): # PUT method = Update item via SQL update
        print("Damper PUT called: "+ str(record_id))
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = DamperSchema().load(args) # Deserialize data structure to an object defined by this Schema’s fields types and formats, e.g. convert str "dates" to datetime
        schema["updated_at"] = datetime.now() # update timestamp to current date & time

        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.query(Damper).filter_by(id=record_id).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update
        session.commit() # Write to database
        session.close() # Close session
    
        return record_id 

    def delete(self, record_id): # DELETE method = delete existing item
        print(f'Damper DELETE called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Damper).get(record_id)  # Get record 
        session.delete(db_object)  # Delete record
        session.commit() # Write to database
        session.close() # Close session

        return record_id


class ReportREST(Resource):  #REST API for reports: GET/POST/PUT/DELETE
    def get(self, record_id): # GET method = read existing item
        print(f'Report GET called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Report).get(record_id)  # Get record 
        session.close() # Close session

        schema = ReportSchema(many=False)
        py_object = schema.dump(db_object) # Dump = Serialize an object to native Python data types according to this Schema’s fields. Returns a dict of serialized data
        print('Got 1 report:', py_object)

        return jsonify(py_object) # Supercharged Flask method to convert to  JSON and add the mimetype application/JSON

    def post(self, record_id):   # POST method = Create new item
        print("Report POST called")
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = ReportSchema().load(args)  # Load = Deserialize a data structure to an object defined by this Schema’s fields. Returns a dict of deserialized data
        py_object = Report(**schema) # The ** notation is "unpacking" the dictionary into keyword argument for the function call
     
        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.add(py_object) # The add function gets the table name from the object.
        session.commit() # Write to database
        new_id = py_object.id  # This is the auto generated new primary key ID of the just added record
        session.close()

        return new_id 

    def put(self, record_id): # PUT method = Update item via SQL update
        print("Report PUT called: "+ str(record_id))
        args = request.get_json() # extract JSON from HTTP querry and convert it to Python dict
        schema = ReportSchema().load(args) # Deserialize data structure to an object defined by this Schema’s fields types and formats, e.g. convert str "dates" to datetime
        schema["updated_at"] = datetime.now() # update timestamp to current date & time

        Base.metadata.create_all(engine) # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        session.query(Report).filter_by(id=record_id).update(schema) # Update record via SQL Expression, as there is no ORM equivalent for update
        session.commit() # Write to database
        session.close() # Close session
    
        return record_id 

    def delete(self, record_id): # DELETE method = delete existing item
        print(f'Report DELETE called with ID: {record_id}')
        Base.metadata.create_all(engine)  # Creates all dbs and tables, which don't exist yet
        session = Session() # start session
        db_object = session.query(Report).get(record_id)  # Get record 
        session.delete(db_object)  # Delete record
        session.commit() # Write to database
        session.close() # Close session

        return record_id


if __name__ == '__main__':
    ### When routing is done via classes, the route must be added here
    ### (If routing is done via functions, the route is added as a decorator to the function):
    api.add_resource(Dampers, '/dampers') # returns all "Damper" objects
    api.add_resource(Commission, '/commission') # Adds new dampers. Currently only virtual damper objects are generated. TO DO: define real world commissioning
    api.add_resource(CreateGroup, '/creategroup') # Generates a new "Group"
    api.add_resource(Groups, '/groups') # returns all "Group" objects
    api.add_resource(Tests, '/tests') # returns all "Test" objects
    api.add_resource(Reports, '/reports') # returns all "Report" objects
    api.add_resource(GetGroup, '/getgroup/<int:record_id>') # returns one "Group" object
    api.add_resource(SaveGroup, '/savegroup') # Updates damper group memebership, group name and creates a new group if necessary
    api.add_resource(ControllerREST, '/controller/<int:record_id>') # REST API for controllers
    api.add_resource(TestREST, '/test/<int:record_id>') # REST API for tests
    api.add_resource(DamperREST, '/damper/<int:record_id>') # REST API for dampers
    api.add_resource(ReportREST, '/report/<int:record_id>') # REST API for reports
    # api.add_resource(ControllerREST, '/controller') # REST API for controllers: Returns ALL controllers in db

    socketio.run(app, debug=True, host="0.0.0.0", port=5002)

    # This line starts the server during development. Probably needs to be started differently:
    # app.run(host= '0.0.0.0',port=5002)      
    # if __name__ == '__main__':
    #      app.run(port=5002)

    # This starts teh server during the development, and additionally allows websocket connections:
    # if __name__ == '__main__':
    #     socketio.run(app, debug=True, host="0.0.0.0")
