import io,os,sys
import datetime
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def readConfig(fold='.',fname=''):
        # read the configuration file
        config={}
        if fname=='':
            if os.path.exists(fold+os.sep+'config.txt'):
                fh=open(fold+os.sep+'config.txt','r')
            else:
                print('configuration file does not exists. for test purposes it can continue')
                return config
        else:
            fh=open(fname,'r')
        righe=fh.readlines()
        config['pressureSensor']=''
        config['Tail']=''       
        config['TailSimple']=''
        config['folderWWW']=''
        config['ReadFile']=''
        config['PhotoCMD']=''
        config['PhotoAlertLevel']=10
        config['PhotoTimeInterval']=2
        config['MQTT_server']=''
        config['MQTT_listener']=''        
        config['MQTT_username']='' 
        config['MQTT_password']='' 
        config['MQTT_msg']=''
        config['ADC_1']=106
        config['ADC_2']=105
        config['scrapePage'] =''
        config['TCP_host']=''

        for  riga in righe:
                #print(riga)
                if not riga.startswith('*'):
                        if '=' in riga:
                                tag=riga.split('=')[0].strip()
                                value=riga[riga.find('=')+1:].strip().replace('\n','')
                                #value=riga.split('=')[1].split('*')[0].strip()
                                #print (tag,value)
                                config[tag]=value

        fh.close()


        return config

def prepareFolders(fname):
        multY = 1.0
        vminDev = -10
        vmaxDev = 10
        ncols = -1
        multicols = False
        multicolsBIG = False
        provider = ""
        typePlot = ""
        region0=''
        with open (fname) as f:
            testo = f.read().split('\n')
#        if InStr(testo0, "jsonurl") <> 0 :
#            jsonurl = Split(Split(testo0, "jsonurl=")(1), vbCrLf)(0)
#            testo0 += getListNOAA(jsonurl)


#        End if
#        File.WriteAllText(startupPath() & "listLocations0.txt", testo0)
        
        ntotDev = len(testo) - 2
        nbat = int(ntotDev / 50) + 1
        if nbat < 1: nbat = 1
        for f in ("sqlText.txt","sqlDeviceFieldsMap.txt","sqlDeviceFieldsMap.txt"):
            if os.path.exists(f):
                os.remove(f)
        n = 0
        ngr = 1
        ndev = 0
        for line in testo:
            if line == "":continue
            if line[0] == "*":continue
            if line[0]== "$":
                p = line.split("$")[1].strip().split('\t')
                for  d in p:
                    if d == "": continue
                    key=d.split('=')[0]
                    value=d[d.find('=')+1:].strip()
                    
                    if key == "mode":
                        mode = value
                    elif key == "type":
                        type = value
                    elif key == "outSRV":
                        outSrv = value
                    elif key == "provider" :
                        provider = value
                    elif key == "typePlot":
                        typePlot = value
                    elif key == "ng":
                        ng = value
                    elif key == "vmin":
                        vminDev = value
                    elif key == "vmax":
                        vmaxDev = value
                    elif key == "multY" :
                        multY = value
                    elif key == "prefixURL" :
                        prefixURL = value

                    elif key == "jsonurl" :
                        url = value
                    elif key == "multicols" :
                        multicols = (value == "True")
                    elif key == "multicolsBIG" :
                        multicolsBIG = (value == "True")
                    
                for nn in range(nbat):
                    with open("run_" + type + "_" + format(nn ) +".sh",'w') as f:
                        f.write("echo %DATE% %TIME% START BATCH >> logCalls.txt  \n")
                if provider == "" :
                    provider = type
            
                if typePlot == "" :
                    typePlot = type

                continue
            
            pars = line.split('\t')
            
            lat = pars[0].strip()
            lon = pars[1].strip()
            country = pars[2].strip()
            name = pars[3].strip()
            if '"' in country :
                country = country.replace('"','')
            if '"' in name :
                name = name.replace('"','')

            link = pars[4].strip()
            code = pars[5].strip()
            if len(pars) >= 6 :
                region = pars[6].strip()


            if multicols and False :
                urlcsv = prefixURL + link
                urlcsv=urlcsv.replace('$DAY',datetime.datetime.utcnow().strftime('%Y-%m-%d'))
                response=urlopen(urlcsv)
                testo1=response.read().decode("utf-8")
                if testo1 != "" :
                    ncols = len(testo1.split('\n')[0].split(','))

            #if multicolsBIG :
            #    ncols = 3
            if multicols:
                ncols=3
            conf = ""
            conf += "title         = " + name +'\n'
            conf += "location      = " + lat + "," + lon +'\n'
            conf += "IDdevice      = " + code +'\n'
            conf += "serverAddress = " + prefixURL +link.replace('=',"$EQ") +'\n' #'&period$EQ30&starttime$EQ$START"
            conf += "ServerPort    = 0" +'\n'
            conf += 'OutFolder     = .\\logs\\\n'
            if multicols or multicolsBIG :
                conf += "ncols         = " +format( ncols) +'\n'
                if ncols == 2 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$LEV_2,$FORE30_2,$FORE300_2,$RMS_2,$ALERT_LEVEL_2,$ALERT_SIGNAL_2,0,0,0,0,0,0,$V1,$V2,$E" +'\n'
                elif ncols == 3 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$LEV_2,$FORE30_2,$FORE300_2,$RMS_2,$ALERT_LEVEL_2,$ALERT_SIGNAL_2,$LEV_3,$FORE30_3,$FORE300_3,$RMS_3,$ALERT_LEVEL_3,$ALERT_SIGNAL_3,$V1,$V2,$E" +'\n'
                elif ncols == 1 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$V1,$V2$E" +'\n'
                else:
                    print('errore')
                    quit()
                
            else:
                conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$V1,$V2,$E" +'\n'
            

            conf += "AlertURL      = " + outSrv + "/SensorGrid/EnterAlert.aspx?idDevice=$IDdevice&AlertLevel=$ALERT_SIGNAL&DateTime=$DATE $TIME&SignalType=TAD&AlertType=AUTO" +'\n'
            conf += "DataFile      = Data_yyyyMMdd.txt" +'\n'
            conf += "Datalog       = dataLog_yyyyMMdd.txt" +'\n'
            conf += "Interval      = -1" +'\n'
            if multY != 1 :
                conf += "MultY      = " & multY +'\n'

            conf += "n300          =  100" +'\n'
            conf += "n30           =  10" +'\n'
            conf += "threshold     = 0.1" +'\n'
            conf += "ratioRMS      = 3" +'\n'
            conf += "AddRMS        = 0.1" +'\n'
            conf += "backFactor    = 0" +'\n'
            conf += "vmin          = " + format(vminDev) +'\n'
            conf += "vmax          = " + format(vmaxDev) +'\n'
            conf += "remAndInvert  = 0." +'\n'
            conf += "mode          = " + mode +'\n'
            conf += "scrapePage          = " + type +'\n'
            conf += "settingsFile  = ..\settings.txt" +'\n'
            if not os.path.exists(".\\" + code) :
                os.makedirs(".\\" + code )
            with open (".\\" + code + "\\config.txt",'w') as f:
                f.write(conf)

            linetoadd = "INSERT INTO [dbo].[devices] ([DeviceName],[Location] ,[lat],[lon],[Type],[status],[CountryM],[RegionM],[groupId],[Provider],[ConsistencyCheck],[Notes],[TypePlots])"
            linetoadd += " VALUES ('" + code + "' "

            linetoadd += ",'" +name.replace("'" ,"''")+ "'"
            linetoadd += "," + format(lat)
            linetoadd += "," + format(lon)
            linetoadd += ",2"
            linetoadd += ",'active'"
            linetoadd += ",'" + country + "'"
            linetoadd += ",'" + region + "'"
            linetoadd += "," + format(ng)
            linetoadd += ",'" + provider + "','N'," + "'" + type + "',"
            if multicols or multicolsBIG :
                linetoadd += "'" + typePlot + "_" + format(ncols) + "' )"
            else:
                linetoadd += "'" + typePlot + "' )"

            with open ("sqlText.txt",'w') as f:
                f.write(linetoadd +'\n')

            n += 1
            ndev += 1
            print(format(ndev) + " " + country + " " + name + " ncols=" + format(ncols))
            nb = int(ndev / ntotDev * nbat)
            batTxt = "cd " + code +'\n'
            #batTxt += "copy /y ..\gaugeListener.exe ." +'\n'
            #batTxt += "gaugeListener.exe" +'\n'
            #batTxt += "set / p lastValue=<lastValue.txt" +'\n'
            #batTxt += "echo %DATE% %TIME% %lastValue% >> logCalls.txt" +'\n'
            #batTxt += "cd .." +'\n' +'\n'

            #File.AppendAllText("run_" + type + "_" & nb & ".sh", batTxt)


            linetoadd = "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Value', 'anag2', 0, '' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Level', 'inp1', 1, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'RMS', 'inp4', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast30', 'inp2', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast300', 'inp3', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Level', 'anag1', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'

            
            with open ("sqlDeviceFieldsMap.txt",'w') as f:
                f.write(linetoadd +'\n')

            if region != region0 or region0 == "" :
                ngr += 1
                linetoadd = "INSERT INTO [dbo].[groups] ([ID], [GroupName], [Note], [Color]) VALUES (" +format( ngr )+ ", '" + region + "' ,'Indonesia Region " + region + "' ,'" + format(ngr * 5) + ",0,255')" +'\n'
                region0 = region
                
                with open ("sqlGroups.txt",'w') as f:
                    f.write(linetoadd +'\n')

            tp = type
            if ncols > 1 :
                tp += "_" + format(ncols)

            linetoadd = "update devices set typePlots='" + tp + "',countryM='" + country + "',regionM='" + region + "', groupID=" +format( ngr  )+ " where deviceName='" + code + "'" +'\n'
            
            with open ("sqlupdateDevices.txt",'w') as f:
                f.write(linetoadd +'\n')

        
        linetoadd = "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',1,'Water Level','Measured Water Level','Water Level (m)','inp1',NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',2,'Forecast','Forecast 30 (red) - Forecast 300 (blue)','Forecast 30','inp2','Forecast300','inp3',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',3,'Rms Alert Signal','Rms (blue) - Alert Signal (red) - Rms Limit (green)','Alert Level (m)','anag1','RMS','inp4',0,NULL,'Calc','inp4*4+0.1',NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',4,'Alert Level','Alert Level (0-10)','Alert Level (-)','anag2',NULL,NULL,0,NULL,NULL,NULL,'0;11;1',NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',7,'Latency','Data Latency','Latency (s)','datediff(second,[Date],[UpdateTime])',NULL,NULL,0,NULL,NULL,NULL,NULL,'0;600;50',NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',1,'Water Level','Measured Water Level','Water Level (m)','inp1',NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'

        linetoadd += "INSERT INTO [dbo].[groups] ([ID], [GroupName], [Note], [Color]) VALUES (" + format(ng) + ", '" + type + "' ,'" + type + "' ,'255,0,255')"

        
        with open ("sqlPlots.txt",'w') as f:
            f.write(linetoadd +'\n')

def getListNOAA(URL):
        import requests
        resp=requests.get(URL)
        stations = resp.json()['stations']
        testo = ""
        vbTab='\t'
        for station in stations:
            print(format(station['lat']) + "," + format(station['lng']) + "," + station['name'] + " " + station['id'])
            #'*lat	lon	Country	name	filename	code
            testo += format(station['lat']) + vbTab + format(station['lng']) + vbTab +"United States" + vbTab + station['name'] +vbTab
            testo += "https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&begin_date=$BEGINDATE&end_date=$ENDDATE&datum=MSL&station=" + station['id'] + "&time_zone=GMT&units=metric&format=json" + vbTab
            newID = station['name'].split(",")[0].replace(" ", "_").replace(".", "")
            if newID == "Charleston" and ',' in station['name'] :
                newID += "_" + station['name'].split(",")[1].replace(" ", "_").replace(".", "")
            
            testo +='NOAA-'+newID
            testo += vbTab + station['id'] +'\n'
        return testo

if __name__ == "__main__":
    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    for k in range(len(arguments)):
        arg=arguments[k]
        if arg=='-c':
            os.chdir(arguments[k+1])
            print("Current working directory: {0}".format(os.getcwd()))
        if arg=='-noaa':
            with open('listLocations.txt') as f:
                rows=f.read().split('\n')
            testo=''
            for r in rows:
                if r.strip().startswith('$'):
                    keys=r.split('\t')
                    for j in range(len(keys)):
                        if keys[j].split('=')[0]=='jsonurl':
                            jsonURL=keys[j].split('=')[1]
                    testo +=r+'\n'
                    testo +='*************************************************'
                    testo+=getListNOAA(jsonURL)
                    break       
                else:
                    testo+=r+'\n'
            with open('listLocations.txt','w') as f:
                f.write(testo)
        if arg=='-s':
            prepareFolders('listLocations.txt')

def virtualConfig(arguments):
    config={}
    config['pressureSensor']=''
    config['Tail']=''       
    config['TailSimple']=''
    config['folderWWW']=''
    config['ReadFile']=''
    config['PhotoCMD']=''
    config['PhotoAlertLevel']=10
    config['PhotoTimeInterval']=2
    config['MQTT_server']=''
    config['MQTT_listener']=''        
    config['MQTT_username']='' 
    config['MQTT_password']='' 
    config['MQTT_msg']=''
    config['ADC_1']=106
    config['ADC_2']=105
    config['scrapePage'] =''
    config['TCP_host']=''
    config['vmin']=-10
    config['vmax']=10
    IDdevice=''
    outFolder='/'
    for j in range(len(arguments[1:])):
        if arguments[j]=='-code':
                code=arguments[j+1]
        if arguments[j]=='-IDdevice':
                IDdevice=arguments[j+1]
        if arguments[j]=='-n30':
                n30=int(arguments[j+1])
        if arguments[j]=='-n300':
                n300=int(arguments[j+1])
        if arguments[j]=='-mult':
                mult=float(arguments[j+1])
        if arguments[j]=='-add':
                addRMS=float(arguments[j+1])
        if arguments[j]=='-th':
                th=float(arguments[j+1])
        if arguments[j]=='-mode':
                mode=arguments[j+1]
        if arguments[j]=='-out':
                outFolder=arguments[j+1]
   #  example of call  python3 scrape.py -idDevice adak -code  adak  -n300 150  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode GLOSS -out e:/temp

    if IDdevice=='':  IDdevice=code
    config['IDdevice']=IDdevice
    config['Interval'] = -1
    config['n300']=n300
    config['n30']=n30
    config['threshold']=th
    config['ratioRMS']= mult
    config['AddRMS']=addRMS
    config['SaveURL']=''
    config['AlertURL']=''
    config['AlertLevel']=2
    config['outFolder']=outFolder
    if mode=='GLOSS':
        config['serverAddress']='https://www.ioc-sealevelmonitoring.org/service.php?query=data&format=xml&code='+code+'&period=7'
    elif mode=='NOAA':
        config['serverAddress']='https://tidesandcurrents.noaa.gov/api/datagetter?product$EQwater_level&application$EQNOS.COOPS.TAC.WL&begin_date$EQ$BEGINDATE&end_date$EQ$ENDDATE&datum$EQMSL&station$EQ'+code+'&time_zone$EQGMT&units$EQmetric&format$EQjson'        
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    with open(outFolder+os.sep+'config.txt','w') as f:
        for key in config.keys():
            f.write(key+'='+format(config[key])+'\n')
    return config