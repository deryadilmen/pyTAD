from dashImport import app,html,dcc
from dash.dependencies import Input, Output,State
import os
from datetime import datetime,timedelta
from utilities import getList,getData
from calcAlgorithm import calcAlgorithm as ca

from utilities import getData,getValues,getFigure
data=getData('JRC_TAD')

app.layout = html.Div([ 
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

appserver=app.server

@app.callback(Output('page-content', 'children'),
            Input('url', 'pathname'),Input('url', 'href'))
def display_page(pathname,url):
    authState=False
    
    print('PID=....',os.getpid())
    listNmax=[]
    n=1000;listNmax.append({'label':n,'value':n})
    n=5000;listNmax.append({'label':n,'value':n})
    n=10000;listNmax.append({'label':n,'value':n})
    n=15000;listNmax.append({'label':n,'value':n})
    n=20000;listNmax.append({'label':n,'value':n})
    n=30000;listNmax.append({'label':n,'value':n})
    n=40000;listNmax.append({'label':n,'value':n})
    n=50000;listNmax.append({'label':n,'value':n})
    n=75000;listNmax.append({'label':n,'value':n})
    n=100000;listNmax.append({'label':n,'value':n})
    lg=getList('GROUPS',data)
    lg1=[]
    selectDevice=html.Table([
            html.Tr([html.Td('Group'),html.Td('Device'),html.Td('')]),
            html.Tr([
                html.Td(dcc.Dropdown(id='GROUPS',options=lg,style={'width':'200px'})),
                html.Td(dcc.Dropdown(id='DEVICES',options=lg1,style={'width':'600px'})),
                html.Td(dcc.Dropdown(id='numMaxdata',options=listNmax,style={'width':'400px'})),
                html.Td(html.Button('Get Data',id='getData',n_clicks=-1))
                ])            
            ])

    paramsModel=html.Table([
        html.Tr([html.Td('n300'),
                 html.Td('n30'),
                 html.Td('threshold'),
                 html.Td('ratioRMS'),
                 html.Td('AddRMS'),
                 #html.Td(html.Button('Calculate',id='calcData',n_clicks=-1))
                 ]),
        html.Tr([html.Td(dcc.Input(id='n300',value=300)),
                 html.Td(dcc.Input(id='n30',value=30)),
                 html.Td(dcc.Input(id='threshold',value=0.1)),
                 html.Td(dcc.Input(id='ratioRMS',value=4)),
                 html.Td(dcc.Input(id='AddRMS',value=0.08))
                 ]),
        html.Tr(html.Td(html.Div(id='status'),style={'colspan':5}))
            ])
    graf=html.Div('',id='grafici')
    layout=html.Div([selectDevice,html.Br(), paramsModel,html.Br(),graf])    
    
    return  layout


@app.callback(Output('DEVICES','options'),Input('GROUPS','value'))

def selgroup(groupID):
    options=getList('DEVICES',data,groupID)
    return options

@app.callback(Output('grafici','children'),Output('status','children'),
              Input('getData', 'n_clicks'),
              State('DEVICES','value'), State('n300','value'), 
              State('n30','value'), State('threshold','value'), State('ratioRMS','value'),
              State('AddRMS','value'), State('numMaxdata','value'))

def updatePlots(nclick,deviceID,n300,n30,threshold,ratioRMS,addRMS,nmaxData):
    if deviceID=='' or deviceID==None:
        return '','select a device with data'
    n300=int(n300)
    n30=int(n30)
    tmax=datetime.utcnow()
    tmin=tmax-timedelta(days=0.1)
    values, avgDelta=getValues('JRC_TAD',deviceID, tmin, tmax, 500000)  
    
    tmin=tmax-timedelta(days=3)
    values, avgDelta1=getValues('JRC_TAD',deviceID, tmin, tmax, nmaxData)  
    try:
        status='delta/orig Delta Status: '+format(round(avgDelta/avgDelta1,2))+' n300 and n30 will be adjusted accordingly, n300='+format(int(n300*avgDelta/avgDelta1))
    except Exception as e:
        status=e
    print(n300, avgDelta, avgDelta1)
    n300=int(n300*avgDelta/avgDelta1)
    n30=int(n30*avgDelta/avgDelta1)
    config={}
    config['Interval']=-1
    config['n30']=n30
    config['n300']=n300
    config['ratioRMS']=float(ratioRMS)
    config['threshold']=float(threshold)
    config['AddRMS']=float(addRMS)
    config['vmin']=-1e9
    config['vmax']=1e9
    config['SaveURL']=''
    import os 
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fold=dir_path+os.sep+'temp'
    if not os.path.exists(fold):
        os.makedirs(fold)
    calg=ca(0,fold,config)
    values['fore30']=[]
    values['fore300']=[]
    values['rms']=[]
    values['rmsMod']=[]
    values['alertSignal']=[]
    values['alertValue']=[]
    print(len(values['x']))
    for j in range(len(values['x'])):
        tim=values['x'][j]
        measure_Float=values['y'][j]
        forecast30,forecast300,rms,alertSignal,alertValue= calg.addMeasure(tim,measure_Float,fold,0)
        values['fore30'].append(forecast30)
        values['fore300'].append(forecast300)
        values['rms'].append(rms)
        values['rmsMod'].append(rms*ratioRMS+addRMS)
        values['alertSignal'].append(alertSignal)
        values['alertValue'].append(alertValue)
        if int(j/200)*200==j:
            print(j,len(values['x']))
    print(len(values['x']),len(values['fore30']))
    fig1=getFigure(values,[('x','y')])
    fig2=getFigure(values,[('x','y'),('x','fore30'),('x','fore300')])
    fig3=getFigure(values,[('x','rms'),('x','alertSignal'),('x','rmsMod')])
    fig4=getFigure(values,[('x','alertValue')])

    grafico1=dcc.Graph(id='plot1', figure=fig1)
    grafico2=dcc.Graph(id='plot2', figure=fig2)
    grafico3=dcc.Graph(id='plot3', figure=fig3)
    grafico4=dcc.Graph(id='plot4', figure=fig4)

    return html.Div([grafico1,grafico2,grafico3,grafico4]),status


if __name__ == '__main__':
    print('PID=',os.getpid())

    appserver=app.server
    app.run_server(debug=True)