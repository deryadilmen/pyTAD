
from CONF import config, folderOut
import json,os,sys
from datetime import datetime, timedelta
import time
from urllib.request import urlopen
import urllib

from alerts import checkAlerts

from readConfig import readConfig
import requests

import xml.etree.ElementTree as ET
import urllib.parse, urllib.request, urllib.error



def saveData(config,wgetData,folderOut,tt,press,temp,measure_Float,forecast30,forecast300,rms,alertValue,alertSignal,batt,tempCPU,temp380):
        SaveURL=config['SaveURL']
        SaveURL=SaveURL.replace('$EQ','=')
        SaveURL=SaveURL.replace('\$','$')
        #print SaveURL
        idDevice=config['IDdevice']
        if '$HOSTNAME' in idDevice:
            idDevice=idDevice.replace('$HOSTNAME',os.uname()[1])
        #idDevice=idDevice.replace('$HOSTNAME',socket.gethostname())
        #idDevice=idDevice.replace('$HOSTNAME','IDSL-50x')
        #print idDevice
        SaveURL=SaveURL.replace('$IDdevice',idDevice)
        #print SaveURL 
        SaveURL=SaveURL.replace('$DATE',format(tt,'%d/%m/%Y'))
        SaveURL=SaveURL.replace('$TIME',format(tt,'%H:%M:%S'))
        SaveURL=SaveURL.replace('$TEMP','22')
        SaveURL=SaveURL.replace('$PRESS','908')
        SaveURL=SaveURL.replace('$LEV',"%.3f" % measure_Float)
        SaveURL=SaveURL.replace('$FORE300',"%.3f" % forecast300)
        SaveURL=SaveURL.replace('$FORE30',"%.3f" % forecast30)
                
        SaveURL=SaveURL.replace('$RMS',"%.4f" % rms)
        SaveURL=SaveURL.replace('$ALERT_SIGNAL',"%.3f" % alertValue)
        SaveURL=SaveURL.replace('$ALERT_LEVEL',"%.3f" % alertSignal)
        SaveURL=SaveURL.replace('$V1','%.2f' % batt)
        SaveURL=SaveURL.replace('$V2','%.1f' % 0.0)
        SaveURL=SaveURL.replace('$V3','%.3f' % tempCPU)
        SaveURL=SaveURL.replace('$V4','%.3f' % temp380)

        SaveURL=SaveURL.replace('$V1','0')
        SaveURL=SaveURL.replace('$V2','0')
        SaveURL=SaveURL.replace('$V3','0')
        SaveURL=SaveURL.replace('$V4','0')
        SaveURL=SaveURL.replace('$V5','0')
                
        #cmd='wget "'+SaveURL+'" -T 2 -r 1 -nv -o outlogwget.txt'
        #cmd='wget "'+SaveURL+'" -nv -o '+folderOut+'/outlogwget.txt -O '+folderOut+'/outwget.txt'
        #print (SaveURL)

        wgetData.append(SaveURL)
        #print(tt,mavg)
        try:
            riga='time='+format(tt,'%d/%m/%y %H:%M:%S')+'\n'
            riga+='Level (m)='+"%.3f" % measure_Float +'\n'
            riga+='Short Term forecast='+"%.3f" % forecast30+'\n'
            riga+='Long Term forecast='+"%.3f" % forecast300+'\n'
            riga+='RMS='+"%.4f" % rms+'\n'
            riga+='Alert Value='+"%.3f" % alertValue+'\n'
            riga+='Alert Signal='+"%.3f" % alertSignal+'\n'
        
            if 'folderWWW' in config:
                folderWWW=config['folderWWW']
                f1=open(folderWWW+os.sep+'CurrentData.txt','w')
                f1.write(riga)
                f1.close()
            #riga+=format(nd1)
                    
            riga=SaveURL.split('log=')[1].replace('$S','').replace('$E','')
            checkAlerts(config,tt,measure_Float,alertValue, folderOut)

            print(riga)
                    
            fname=folderOut+os.sep+'execLog_'+datetime.strftime(tt,'%Y-%m-%d')+'.txt'
            f1=open(fname,'a')
            f1.write(riga+'\n')
            f1.close()
            with open(folderOut+os.sep+'lastRead.txt','w') as f1:
                f1.write(datetime.strftime(tt,'%Y-%m-%d %HH:%MM:%SS'))
        except Exception as e:
            print(e)

def scrape_init(config,wgetData,folderOut):
    from  process import addMeasure
    from calcAlgorithm import calcAlgorithm as ca
    session_requests = requests.session()
    tt='';measure_Float=''
    sl=config['scrapeLogin'] #"http://202.90.199.202/tntmon/loginauth.php"
    if '@http' in sl:
        login_url=sl.split('@')[1]
        uname=sl.split('@')[0].split(':')[0]
        pwd=sl.split('@')[0].split(':')[1]
        payload={ "username":uname,"password":pwd, "submit":"Login"}
    else:
        login_url=sl
    while True:
        login_ref=login_url 
        result = session_requests.get(login_url)

        result = session_requests.post(
            login_url,
            data = payload,
            headers = dict(referer=login_ref)
        )
        res=result.content
        fnameOut=folderOut+os.sep+config['IDdevice']+'.txt'
        if os.path.exists(folderOut+os.sep+'lastRead.txt'):
            try:
                with open(folderOut+os.sep+'lastRead.txt') as f1:
                    lr=f1.read()
                lastread=datetime.strptime(lr,'%Y-%m-%d %HH:%MM:%SS')
            except:
                lastread=datetime(2022,1,1)  
        else:
            lastread=datetime(2022,1,1)  
        
        while True:
            t0=datetime.utcnow()-timedelta(seconds=3600)
            t1=datetime.utcnow()
            tstart=t0.strftime('%Y-%m-%d %H:%M:%S')
            tend=t1.strftime('%Y-%m-%d %H:%M:%S')

            url=config['scrapePage'] 
            url=url.replace('$DATESTART',tstart)
            url=url.replace('$DATEEND',tend)
            url=url.replace('$EQ','=')
            print(url)
            try:
                result = session_requests.get(
                     url,
                     headers = dict(referer = url)
                )
            except:
                break
            res=result.content
            if res.decode() !='':
                js=json.loads(res)

                radData=js['DATA']['RAD']
                #preData=js['DATA']['BAR']
        
                f=open(fnameOut,'a')
                for j in range(len(radData)):
                
                    rd=radData[len(radData)-j-1]
                    t,v=rd
            
                    try:
                        tt = datetime.fromtimestamp(t/1000)- timedelta(seconds=2*3600)
                        measure_Float=float(v)
                        #print(format(tt)+', '+format(measure_Float))
                    except:
                        print('errore',t,measure_Float)
                    
                    if tt>lastread:
                        f.write(format(tt)+' '+format(measure_Float)+'\n')
                        lastread=tt
                        forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(config,tt,measure_Float,folderOut)
                        saveData(config,wgetData,folderOut,tt,908,22,measure_Float,forecast30,forecast300,rms,alertValue,alertSignal,0,0,0)

                        time.sleep(0.05)
                    
                f.close()
    
            print('Sleeping 1 min , last values ', format(tt)+' '+format(measure_Float))
            time.sleep(60)
        time.sleep(60)   

def scrape_TCP(config,queueData,folderOut):
    import socket,time

    #HOST = '62.48.216.99'  # Standard loopback interface address (localhost)
    #PORT = 4001  # Port to listen on (non-privileged ports are > 1023)
    HOST=config['TCP_host']
    PORT=int(config['TCP_port'])
    while True:
        t0=datetime.utcnow()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                try: 
                    data = s.recv(1024).decode()
                    connected=True
                except socket.error as msg:
                    print("disconnected")
                    s.close()
                    connected=False
                if connected:            
                    if config['TCP_type']=='SECIL':
                        levs=data.split('\n\r')
                        for lev in levs:
                            if lev !='':
                                tt=datetime.utcnow()
                                queueData.append((tt,float(lev)))
                                fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                                fh=open(fname,'a')
                                fh.write(format(tt)+' '+format(lev)+'\n')
                                fh.close()
                                #print(tt,lev)
                                #forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(tt,lev,folderOut)
                                #saveData(config,wgetData,folderOut,tt,908,22,lev,forecast30,forecast300,rms,alertValue,alertSignal,0,0,0)     
                    time.sleep(0.1)
                    t1=datetime.utcnow()
                    print('time from opening: ',(t1-t0).seconds)
                    if (t1-t0).seconds>3600:
                        print('close connection and restart')
                        break
                else:
                    break
        time.sleep(1)       

def saveSamples(config,calg,data,ncols,folderConfig, folderOut):
    from  process import addMeasure,readBuffer,saveBuffer
    logData=''
    kj=-1
    for tim,samp in data:
        logDataAdd=''
        for k in range(ncols):
            if ncols>1:
                measure_Float=samp[k]
            else:
                measure_Float=samp
            try:
                forecast30,forecast300,rms,alertSignal,alertValue= calg[k].addMeasure(tim,measure_Float,folderConfig,k)
                checkAlerts(config ,tim, measure_Float, alertSignal,folderConfig)
                logDataAdd = calg[k].prepareString(k,config, tim, measure_Float,forecast30,forecast300,rms,alertSignal,alertValue, logDataAdd)
                saveBuffer(calg[k]._x300,calg[k]._y300,calg[k]._yavg30,calg[k]._yavg300,folderConfig,k)
            except Exception as e:
                print(e)
        logDataAdd=logDataAdd.replace('$V1','')
        logDataAdd=logDataAdd.replace('$V2','')
        logDataAdd=logDataAdd.replace('$V3','')
        logData += logDataAdd +'\n'
        print('.......'+logDataAdd[:80])
        fname=folderOut+os.sep+'execLog_'+datetime.strftime(tim,'%Y-%m-%d')+'.txt'
        with open(fname,'a') as f1:
            f1.write(logDataAdd+'\n')

        with open(folderConfig+os.sep+'lastRead.txt','w') as f1:
            f1.write(datetime.strftime(tim,'%Y-%m-%d %HH:%MM:%SS'))
        oldDat = tim
        oldvalue = measure_Float
        newData = True

        #File.WriteAllText("lastValue.txt", Format(tim, "dd MMM yyyy HH:mm") & ", " & Format(value, "#0.00"))
        kj+=1
       
        if (int(kj / 100) * 100 == kj or kj==len(data)-1) and config['SaveURL'] !='':
            URL = config['SaveURL'].split( "log=")[0]+"log=" + logData
            URL = URL.replace("$IDdevice", config['IDdevice'])
            param = URL.split("?")[1]
            params={}
            for keyvalue in param.split('&'):
                key,value=keyvalue.split('=')
                params[key]=value
            URL = URL.split("?")[0]
            data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(URL)
            with urllib.request.urlopen(req,data=data) as f:
                resp = f.read()
            kj=0
            logData=''
            newData=False
    

def scrape_BIG_INA(config,wgetData,folderOut):
    from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    settings=readConfig('',folderConfig+os.sep+config['settingsFile'])
    
    URL=config['serverAddress']    
    URL=URL.replace("$DAY",datetime.utcnow().strftime('%Y-%m-%d'))
    with open(folderConfig+os.sep+'html.htm') as f:
        testo=f.read()
    #response=urlopen(URL)
    #testo=response.read().decode("utf-8")
    tabe = testo.split("<table class='table table-striped'>")[1].split("</table>")[0]
    lines = tabe.split("<tr>")
    ncols=int(config['ncols'])
    
    
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,fold,config,buffer)

    kj=0
    logData = ""
    data=[]
    for line0 in lines[3:]:
        line = line0.replace( "<td>", "")
        if line.strip() != "":
            p = line.split( "</td>")
            tim = datetime.strptime(p[1],'%Y-%m-%d %H:%M:%S')
            print(tim,calg[1]._LastDateTimeAcquired)

            if tim > calg[1]._LastDateTimeAcquired:
                samp=[]
                for k in range(ncols):
                    try:
                        measure_Float = float(p[k +2])
                    except Exception as e:
                            print(e)
                    samp.append(measureFloat)
                data.append((tim,samp))

    saveSamples(config,calg,data,ncols,folderConfig)    
    os.kill(os.getpid(), 9)

def combineDict(a,b):
    for key in b.keys():
        if not key in a:
            a[key]=b[key]
    return a

def scrape_NOAA(config,folderConfig):
    #from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig+os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)
    if 'settingsFile' in config:
        setFile=config['settingsFile'].replace('\\',os.sep)
        settings=readConfig('',folderConfig+os.sep+setFile)
    else:
        settings={}
    today=datetime.utcnow().strftime('%Y%m%d')
    yesterday=(datetime.utcnow()-timedelta(days=1)).strftime('%Y%m%d')
    URL=config['serverAddress']    
    URL=URL.replace("$BEGINDATE",yesterday)
    URL=URL.replace("$ENDDATE",today)
    URL=URL.replace('$EQ', '=')
    resp=requests.get(URL)
    json=resp.json()
    if not 'data'in json:
        print(json)
        return
    samples=json['data']
    ncols=1
    
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    kj=0
    logData = ""
    newData=False
    data=[]
    combConfig=combineDict(config, settings)
    for dat in samples:
        tim = datetime.strptime(dat['t'],'%Y-%m-%d %H:%M')
        try:
            measure_Float = float(dat['v'])
        except:
            print('*** error',dat)
            #print(tim,calg[0]._LastDateTimeAcquired)
        if tim > calg[0]._LastDateTimeAcquired and dat['v']!='':
            data.append((tim,(measure_Float)))

    
    saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    os.kill(os.getpid(), 9)



def scrape_GLOSS(config,folderConfig):
    #from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig +os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    URL=config['serverAddress'] 
    URL=URL.replace('$EQ','=')
    URL=URL.replace('$IDdevice',config['IDdevice'])
    print('opening URL=',URL)
    xmlbin=urllib.request.urlopen(URL).read()
    xmlstr=xmlbin.decode()
    print('len(xmlstr)',len(xmlstr))
    with open('_xml.xml','w') as f:
        f.write(xmlstr)
    #    
    time.sleep(1)    
    print('opening ','_xml.xml')
    tree = ET.parse('_xml.xml')
    os.remove('_xml.xml')
    root=tree.getroot()
    samples=root.findall('sample')
    print('len(samples)',len(samples))
    if len(samples)==0:
        return
    #
    
    ncols=1

#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    for samp in samples:
        tiSt=samp.findall('stime')[0].text
        tim=datetime.strptime(tiSt,'%Y-%m-%d %H:%M:%S')
        try:
            measure_Float = float(samp.findall('slevel')[0].text)
        except:
            print('*** error',samp)
        if tim > calg[0]._LastDateTimeAcquired:
            data.append((tim,(measure_Float)))

#  4)  save the data or print them
    saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    os.kill(os.getpid(), 9)

    

def multi_scrape(idThread,config,wgetData,listConfig):
    from  process import addMeasure
    from calcAlgorithm import calcAlgorithm as ca
    print('****************************************************')
    print('initiating '+idThread+' for ',len(listConfig),' stations')
    print('****************************************************')
    for j in range(len(listConfig)):
        dir=listConfig[j]
        print('\n'+idThread,format(j)+'/'+format(len(listConfig))+':'+dir)
        config=readConfig(dir)
            
        print(' Station: '+dir)
        if config['scrapePage']=='BIG_INA':
            scrape_BIG_INA(config,wgetData,folderOut)
        elif config['scrapePage']=='NOAA':
            scrape_NOAA(config,dir)
        elif config['scrapePage']=='GLOSS':
            scrape_GLOSS(config,dir)        
        time.sleep(1)    


if __name__ == "__main__":

    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    if count<2:
        print('example of call: scrape.py -code  adak  -n300 100  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode GLOSS  -out /temp/adak')
        print('example of call: scrape.py -IDdevice NOAA_Clearance_Water -code  9432780  -n300 100  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode NOAA  -out /temp/Clearance_Water')
    else:
        for j in range(len(arguments[1:])):
            arg,argv=arguments[j:j+2]
        
            if arg=='-mode':
                mode=argv

        if mode=='GLOSS':
            fold=config['outFolder']
            scrape_GLOSS(config,fold)
        elif mode=='NOAA':
            fold=config['outFolder']
            scrape_NOAA(config,fold)
       