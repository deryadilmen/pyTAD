from datetime import datetime
import os,socket
import psutil
import io,sys
import readConfig as rc
from readConfig import virtualConfig



def is_raspberrypi():
    if os.name != 'posix':
        return False
    chips = ('BCM2708','BCM2709','BCM2711','BCM2835','BCM2836')
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    _, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value in chips:
                        return True
    except Exception:
        pass
    return False

import os,sys
from pathlib import Path

from pathlib import Path
parent = Path(__file__).resolve().parent
#print('execution folder',parent)
#  cosi'parto sempre da
os.chdir(format(parent) )
    
machine=socket.gethostname()
#print('machine',machine)
arguments = sys.argv[1:]
folderConfig='./'
listConfigs=[]
NmaxProcs=50
force=False
debugSession=False
virtualConfigFlag=False

for j in range(len(arguments)-1):
    if arguments[j]=='-mode':
        virtualConfigFlag=True
    if arguments[j]=='-d':
        debugSession=arguments[j+1]=='True'

    if arguments[j]=='-c':
        folderConfig=arguments[j+1]
    elif arguments[j]=='-n':
        NmaxProcs=int(arguments[j+1])
    elif arguments[j]=='-f':
        force=(arguments[j+1]=='True')

    elif arguments[j]=='-s':
        folderSettings=arguments[j+1]
        with open(folderSettings+os.sep+'listLocations.txt') as f:
            list=f.read().split('\n')
        listConfigs0=[]
        for r in list[4:]:
            if r !='':
                listConfigs0.append(folderSettings+os.sep+r.split('\t')[5])
                if len(listConfigs0)>=NmaxProcs:
                    listConfigs.append(listConfigs0)
                    listConfigs0=[]
        if len(listConfigs0)>0:
            listConfigs.append(listConfigs0)
        folderConfig=listConfigs[0][0]
if not os.path.exists(folderConfig):
    print('Configuration folder does not exists:'+folderConfig)
    os.kill(os.getpid(), 9)

#print('opening '+folderConfig+os.sep+'config.txt')
if virtualConfigFlag:
    config=virtualConfig(arguments)
else:
    config=rc.readConfig(folderConfig) 

if is_raspberrypi():
    folderData='/tmp/TAD'
    folderOut ='/tmp/pyTAD'
    machine='raspberry'
    folderProg='/home/pi/programs/pyTAD'
else:
    if os.name=='posix':
        folderData='/tmp/TAD'
        folderOut ='/tmp/pyTAD'
        machine='linux'
        folderProg='/mnt/diske/RPI/sowftare/pyTAD'
    else:
        folderData=r'D:/ar   rabsperry/Init Raspberry/Progs/pythonTAD/pyTAD/tmp'
        folderOut=r'D:/ar   rabsperry/Init Raspberry/Progs/pythonTAD/pyTAD/tmpOut'
        folderProg=r'D:/ar   rabsperry/Init Raspberry/Progs/pythonTAD/pyTAD'
        folderWWW=''
        machine='Windows'

if 'folderOut' in config:
    folderOut=config['folderOut']

if not os.path.exists(folderOut):
    os.makedirs(folderOut)
if 'tad.py' in sys.argv[0]:
    if os.path.exists(folderOut+os.sep+'currentProcess.txt'):
        try:
            with open(folderOut+os.sep+'currentProcess.txt','r') as f:
                oldpid=int(f.read())
            print('force=',force)
            if not force:
                if psutil.pid_exists(oldpid):
                    print("tad is already running, pid="+format(oldpid))
                    os.kill(os.getpid(), 9)
                    sys.exit()
            else:
                os.kill(oldpid, 9)
        except:
            print('error reading old pid, continuing')
    
    with open(folderOut+os.sep+'currentProcess.txt','w') as f:
        f.write(format(os.getpid()))

FTP_update_Prog='ftp://139.191.244.76/software/pyTAD.zip'    

queueData=[] #[[1,-1]]*1000
if os.path.exists(folderOut+'/lastTime.txt'):
    f=open(folderOut+'/lastTime.txt','r')
    lastTime=datetime.strptime(f.read(),'%d/%m/%Y %H:%M:%S.%f')
else:
    lastTime=datetime(2020,1,1,0,0)

def printLog(*a):
    try:
        fnameLog=folderOut+os.sep+'logApp.txt'
        f=open(fnameLog,'a')
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(now+': '+  str(a)[1:][:-1] +'\n')
        f.close()
        print(*a)
    except:
        print(*a)