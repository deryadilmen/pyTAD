import os
import time,sys
from datetime import datetime
import subprocess
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def wgetProc(config,wgetData,interval,folderOut,debug=False):
    print ("---------------------------------------------------")
    print ("Starting wgetProcess")
    print ("---------------------------------------------------")

    while True:
        
        if len(wgetData)>0:
            if debug: print ('len wgetdata',len(wgetData))
            #cmd0=wgetData.pop(0)
            try:
                url=wgetData.pop(0)

                if debug: print('opening : '+url)
                response=urlopen(url)
                testo=response.read().decode("utf-8")
                if debug: print(testo)
                #testo=''

            except:
                testo=''
            if not ' OK' in testo:
                print ('data delayed, stored in retry')
                print(testo)
                fh=open(folderOut+'/retry.txt','a')
                fh.write(url+'\n')
            else:
               if debug: print('stored')

            time.sleep(interval)
        #else:
        #     if debug:
        #        return
            
def os_capture(args, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    proc = subprocess.Popen(
        args=args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout = proc.communicate()[0]
  
    return stdout, proc.returncode
    
if __name__ == "__main__":
#    stdout, exit_code = os_capture("wget", "http://webcritech.jrc.ec.europa.eu/TAD_server/Default.aspx?mode=txt&ID=64&ndays=3")
    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    
    if arguments[0]=='RETRY':
        if os.path.exists('retry.txt'):
            f=open('retry.txt') 
            testo=f.read()
            f.close()
            now=datetime.utcnow().strftime('%Y-%m-%d_%H%M')
            os.rename('retry.txt', 'retry_processed_'+now+'.txt')
            wgetData=testo.split('$E')
            for j in range(len(wgetData)):
                wgetData[j] +='$E'
                wgetData[j]=wgetData[j].replace('\n','')
            wgetProc('',wgetData,1,'',True)
    elif arguments[0]=='EXECLOG':
        #  example:  EXECLOG "D:\ar   rabsperry\Init Raspberry\Progs\pythonTAD\pyTAD\DATA\IDSL-309\execLog_2022-05-31.txt"  -tmin "2022-05-31 19:51:00"
        #            EXECLOG "D:\ar   rabsperry\Init Raspberry\Progs\pythonTAD\pyTAD\DATA\IDSL-309\execLog_2022-06-01.txt"  -tmax "2022-06-01 19:51:00"
        fname=arguments[1]
        tmin=datetime(2022,1,1)
        tmax=datetime.utcnow()
        for j in range(len(arguments)):
            if arguments[j]=='-tmin':
                tmin=datetime.strptime(arguments[j+1],'%Y-%m-%d %H:%M:%S')
            if arguments[j]=='-tmax':
                tmax=datetime.strptime(arguments[j+1],'%Y-%m-%d %H:%M:%S')
        if os.path.exists(fname):
            with open(fname) as f:
                rows=f.read().split('\n')
            wgetData=[]
            for row in rows:
                if row=='': continue
                dat=datetime.strptime(row.split(',')[1]+' '+row.split(',')[2],'%d/%m/%Y %H:%M:%S')
                idDevice=row.split(',')[0]
                if dat>=tmin and dat <=tmax:
                    url='http://webcritech.jrc.ec.europa.eu/SensorGrid/EnterData.aspx?idDevice='+idDevice+'&log=$S' + row.split(' (')[0]+'$E'
                    wgetData.append(url)
            wgetProc('',wgetData,0.5,'./',True)
