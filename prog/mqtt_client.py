#  https://logicaprogrammabile.it/mqtt-installare-mosquitto-raspberry-pi-progetti-iot/
#    install mosquitto-raspberry-pi-progetti-iot/
#      sudo apt-get install mosquitto
#  https://antima.it/en/tutorial-using-mqtt-with-python-part-1-the-client-class/
#   install python libraries
#    pip3 install paho-mqtt

from CONF import folderData, folderOut,machine,config
import os,sys,time,json
import uuid
import readConfig as rc
from paho.mqtt.client import Client
from datetime import datetime as datetime,timedelta
if 'MQTT_proxy' in config:
    import socks

_localMsgQueue=[]
_topic='idsl_telemetry'
_debug=False
_connected=False

def on_connect(client, userdata, flags, rc):
    global _connected
    print ("Connected with result code: %s" % rc)
    print('Subscribing to topic ', _topic)
    client.subscribe(_topic)
    _connected=True
    
def on_disconnect(client, userdata, rc):
    global _connected
    print ("Disconnected with result code: %s" % rc)
    _connected=False
  
def init_push(config,queueMQTT,adcData,folderOut):
      global _connected
      print ("---------------------------------------------------")
      print ("Starting MQTT client")
      print ("opening ", config['MQTT_server'],config['MQTT_msg'])
      print ("---------------------------------------------------")

      idDevice=os.uname()[1]
      client=Client(client_id=idDevice)
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      print('Connecting to server ',config['MQTT_server'])
      print('username='+config['MQTT_username']+'<<   pwd='+config['MQTT_password']+'<<')
      if config['MQTT_username'] !='':
        client.username_pw_set(username=config['MQTT_username'],password=config['MQTT_password'])
      print('connecting to MQTT server ',config['MQTT_server'])                    
      client.connect(config['MQTT_server'])
      time.sleep(5)          
      t0=datetime.utcnow()
      try:  
          while True: 
            n=0
            while len(queueMQTT)>0: # or (nd>=len(queueData)-1 and nd>ndata):
                  if (datetime.utcnow()-t0).total_seconds()>3600 and _connected:
                      client.disconnect()
                      _connected=False

                  if not _connected:
                        print('connecting to MQTT server',_connected)                    
                        client.connect(config['MQTT_server'],keepalive=30)
                        time.sleep(1)
                        print('connected',_connected)                    
                        _connected=True
                        t0=datetime.utcnow()
                  #print('before for: ',len(queueMQTT))
                  for j in range(len(queueMQTT)-1):
                      if j<len(queueMQTT):
                        tt,value=queueMQTT[j]
                        queueMQTT.pop(0)
                        PAYLOAD=config['MQTT_msg']
                        PAYLOAD=PAYLOAD.replace('$IDdevice',idDevice)
                        PAYLOAD=PAYLOAD.replace('$DATETIME',format(tt))
                        PAYLOAD=PAYLOAD.replace('$TEMP','%.1f' % float(adcData['tempCPU']))
                        PAYLOAD=PAYLOAD.replace('$PRESS','%.2f' % float(adcData['pressure']))
                        PAYLOAD=PAYLOAD.replace('$LEV',"%.3f" % value)
                        PAYLOAD=PAYLOAD.replace('$BATT','%.2f' % float(adcData['batteryValue']))
                        PAYLOAD=PAYLOAD.replace('$CPUTEMP','%.3f' % float(adcData['tempValue']))
                        PAYLOAD=PAYLOAD.replace('$TEMP380','%.3f' % float(adcData['temperature380']))
                        n+=1
                        if n==20:
                            print(_topic,PAYLOAD)
                            n=0
                        try:
                            client.publish(topic=_topic,payload=PAYLOAD)
                        except:
                            client.disconnect()
                            _connected=False
                        time.sleep(0.05)

            time.sleep(0.1)
      except Exception as e:
            print(e)
            with ('/tmp/stopping_MQTT.txt', 'a') as f:
                  f.write(e)
            os.kill(os.getpid(), 9)
     

def init_listen(config,queueData,adcData,folderOut,proxy='',debug=False):   
        while True:
            print('===============Starting linesting================')
            listen_data(config,queueData,adcData,folderOut,'',debug)
            time.sleep(1)
    
           
def listen_data(config,queueData,adcData,folderOut,proxy='',debug=False):
        print ("---------------------------------------------------")
        print ("Starting MQTT listener")
        print ("opening ", config['MQTT_listener'],config['MQTT_msg'])
        print ("---------------------------------------------------")
        _debug=debug
        if 'MQTT_proxy' in config:
            proxy=config['MQTT_proxy']
        idDevice=config['IDdevice']
        #client=Client(client_id=idDevice)
        print('MQTT: Listening ',config['MQTT_listener'])
        client_id='LISTENER_'+idDevice+'_'+format(uuid.uuid4())
        print('client_id='+client_id)
        client = Client(client_id =client_id) # "sub-test")
        print('username='+config['MQTT_username']+'<<   pwd='+config['MQTT_password']+'<<')
        if config['MQTT_username'] !='':
          client.username_pw_set(username=config['MQTT_username'],password=config['MQTT_password'])

        if not 'MQTT_readDevice' in config:
            config['MQTT_readDevice']=idDevice
        PAYLOAD=config['MQTT_msg']
        indexNames={}
        n=-1
        time.sleep(5)
        for f in PAYLOAD.split('|'):
          n+=1
          indexNames[f.replace('$','')]=n

        def on_connect(client, userdata, flags, rc):
            _connected=True #set flag
            print("Connesso con successo")

        def on_disconnect(client, userdata,  rc):
            _connected=False #set flag
            print("disconnected from mqtt")

        def on_message(client, userdata, message):
            try:
                received_msg = message.payload.decode()
                client_id=client._client_id.decode()
            except Exception as e:
                print('error in received message',e)
                return
            #if _debug: print(received_msg)
            if message.topic == _topic:
                if config['MQTT_readDevice'] in received_msg :
                    _localMsgQueue.append(received_msg)
                    if _debug: print(received_msg)
            else:
                print('discarded '+received_msg)


        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        if proxy !='':
          proxy_host=proxy.split(':')[0]
          proxy_port=int(proxy.split(':')[1])
          client.proxy_set(proxy_type=socks.HTTP, proxy_addr=proxy_host, proxy_port=proxy_port)
        
        client.reconnect_delay_set(min_delay=1)
        client.connect(config['MQTT_listener'])
        
        if 'MQTT_topic'  in config:
            _topic=config['MQTT_topic']
        else:
            _topic='idsl_telemetry'
        client.subscribe(_topic)
        
        client.loop_start()
        time.sleep(5)
        model='IDSL'
        t0=datetime.utcnow()
        if 'MQTT_model' in config:
            model=config['MQTT_model']
        while True:
           t1=datetime.utcnow()
           if not _connected and (t1-t0).total_seconds()>10:
                return
               
           #print(last_msg)
           while len(_localMsgQueue)>0: # or (nd>=len(queueData)-1 and nd>ndata):
              #print('before for: ',len(queueMQTT))
              for j in range(len(_localMsgQueue)):
                try:
                  t0=datetime.utcnow()
                  if j<len(_localMsgQueue):
                    p=_localMsgQueue[j].split('|')
                    _msg=_localMsgQueue[j]
                    _localMsgQueue.pop(0)
                    if model=='IDSL':
                        if len(p)>1: 
                            tt=datetime.strptime(p[indexNames['DATETIME']],'%Y-%m-%d %H:%M:%S.%f')
                            queueData.append((tt,float(p[indexNames['LEV']])))
                            adcData['batteryValue']=p[indexNames['BATT']]
                            adcData['tempValue']=p[indexNames['TEMP']]
                            adcData['tempCPU']=p[indexNames['CPUTEMP']]
                            adcData['pressure']=p[indexNames['PRESS']]
                            adcData['temperature380']=p[indexNames['TEMP380']]
                            adcData['SensorLevel']=p[indexNames['LEV']]
                            fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                           
                            with open(fname,'a') as fh:
                                fh.write(format(tt)+' '+p[indexNames['LEV']]+'\n')
                    elif model=='PUMMA':
                        dd=json.loads(_msg)
                        DA=dd['UTC_Date']+' '+dd['UTC_TS']
                        lev=float(dd['tinggi'])/100.0
                        #tt=datetime.strptime(DA,'%a %b %d %Y %H:%M:%S')-timedelta(seconds=7*3600)
                        tt=datetime.strptime(DA,'%Y-%m-%d %H:%M:%S')+timedelta(seconds=24*3600)
                        
                        queueData.append((tt,lev))
                        if 'tengangan' in dd: adcData['batteryValue']=float(dd['tegangan'])
                        if 'temperature' in dd: adcData['tempValue']=float(dd['temperature'])
                        if 'suhu' in dd: adcData['tempCPU']=float(dd['suhu'])
                        if 'pressure': adcData['pressure']=float(dd['pressure'])
                        adcData['temperature380']=0
                        adcData['SensorLevel']=lev

                            # 'tegangan': 13.4, 'temperature': 32.56, 'humidity': 54.938723240124574, 'pressure': 1009.9360582946874, 'suhu': 44.3}                           
                        fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                       
                        with open(fname,'a') as fh:
                                fh.write(format(tt)+' '+format(lev)+'\n')
                     
                except Exception as e:
                    print(e)
           time.sleep(.2)
           

def init_listen_Multi(config,wgetData,folderOut,proxy='',debug=False):
        print ("---------------------------------------------------")
        print ("Starting MQTT listener multi devices")
        print ("opening ", config['MQTT_listener'])
        print ("---------------------------------------------------")
        _debug=debug
        if 'MQTT_proxy' in config:
            proxy=config['MQTT_proxy']
        print('MQTT: Listening ',config['MQTT_listener'])
        client = Client(client_id ='LISTENER_'+idDevice) # "sub-test")
        print('username='+config['MQTT_username']+'<<   pwd='+config['MQTT_password']+'<<')
        if config['MQTT_username'] !='':
          client.username_pw_set(username=config['MQTT_username'],password=config['MQTT_password'])

        listDevices=config['MQTT_readDevices']
        
        indexNames={}
        n=-1
        time.sleep(5)
        for f in PAYLOAD.split('|'):
          n+=1
          indexNames[f.replace('$','')]=n

        def on_connect(client, userdata, flags, rc):
            print("Connesso con successo")
        def on_message(client, userdata, message):
            received_msg = message.payload.decode()
            client_id=client._client_id.decode()
            #if _debug: print(received_msg)
            print(received_msg)
            if message.topic == _topic:
                for dev in listDevices:
                    if dev in received_msg :
                        _localMsgQueue.append(received_msg)
                    if _debug: print(received_msg)
            else:
                print('discarded '+received_msg)


        client.on_connect = on_connect
        client.on_message = on_message
        if proxy !='':
          proxy_host=proxy.split(':')[0]
          proxy_port=int(proxy.split(':')[1])
          client.proxy_set(proxy_type=socks.HTTP, proxy_addr=proxy_host, proxy_port=proxy_port)

        client.connect(config['MQTT_listener'])
        
        if 'MQTT_topic'  in config:
            _topic=config['MQTT_topic']
        else:
            _topic='idsl_telemetry'
        client.subscribe(_topic)
        client.reconnect_delay_set(min_delay=1, max_delay=12)
        client.loop_start()

        model='IDSL'
        if 'MQTT_model' in config:
            model=config['MQTT_model']
        while True:
           #print(last_msg)
           while len(_localMsgQueue)>0: # or (nd>=len(queueData)-1 and nd>ndata):
              #print('before for: ',len(queueMQTT))
              for j in range(len(_localMsgQueue)-1):
                try:
                  if j<len(_localMsgQueue):
                    p=_localMsgQueue[j].split('|')
                    _msg=_localMsgQueue[j]
                    _localMsgQueue.pop(0)
                    if model=='IDSL':
                        if len(p)>1: 
                            tt=datetime.strptime(p[indexNames['DATETIME']],'%Y-%m-%d %H:%M:%S.%f')
                            queueData.append((tt,float(p[indexNames['LEV']])))
                            adcData['batteryValue']=p[indexNames['BATT']]
                            adcData['tempValue']=p[indexNames['TEMP']]
                            adcData['tempCPU']=p[indexNames['CPUTEMP']]
                            adcData['pressure']=p[indexNames['PRESS']]
                            adcData['temperature380']=p[indexNames['TEMP380']]
                            adcData['SensorLevel']=p[indexNames['LEV']]
                            fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                           
                            with open(fname,'a') as fh:
                                fh.write(format(tt)+' '+p[indexNames['LEV']]+'\n')
                    elif model=='PUMMA':
                        dd=json.loads(_msg)
                        DA=dd['Date']+' '+dd['TS']
                        lev=float(dd['tinggi'])/100.0
                        tt=datetime.strptime(DA,'%a %b %d %Y %H:%M:%S')-timedelta(seconds=7*3600)
                        
                        queueData.append((tt,lev))
                        if 'tengangan' in dd: adcData['batteryValue']=float(dd['tegangan'])
                        if 'temperature' in dd: adcData['tempValue']=float(dd['temperature'])
                        if 'suhu' in dd: adcData['tempCPU']=float(dd['suhu'])
                        if 'pressure': adcData['pressure']=float(dd['pressure'])
                        adcData['temperature380']=0
                        adcData['SensorLevel']=lev

                            # 'tegangan': 13.4, 'temperature': 32.56, 'humidity': 54.938723240124574, 'pressure': 1009.9360582946874, 'suhu': 44.3}                           
                        fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                       
                        with open(fname,'a') as fh:
                                fh.write(format(tt)+' '+format(lev)+'\n')
                     
                except Exception as e:
                    print(e)
           time.sleep(.2)
           
if __name__ == "__main__":
    arguments = sys.argv[1:]

    count = len(arguments)
    print (count)
    
    queueMQTT=[]
    queueData=[]
    adcData={}
    adcData['batteryValue']=-1
    adcData['panelValue']=-1
    adcData['tempValue']=-1
    adcData['tempCPU']=-1
    adcData['pressure']= 0.0
    adcData['temperature380']= 0.0
    adcData['SensorLevel']=-1000
    if arguments[0]=='':        
        init_push(config,queueMQTT,adcData,folderOut)      
    elif arguments[0]=='LISTEN':
        while True:
            listen_data(config,queueData,adcData,folderOut,'',True)
            time.sleep(1)
    elif arguments[0]=='LISTEN_PROXY':
        init_listen(config,queueData,adcData,folderOut,'proxy.JRC.it:8080',True)