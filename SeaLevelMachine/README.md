# The Sea Level Machine ( SLM )

The Seal Level Machine is a web site that visualizes all the Tsunami events occurred since year 2000.  The data are obtained from the NOAA NGDC database (https://www.ngdc.noaa.gov/hazard/tsu_db.shtml). For each event the correspondibng report in the Global Disaster Alerts and Coordination System (GDACS, http://www.gdacs.org) is identified and connected.  This allows to extract the GTS message that were produced by the Tsunami Service Providers for that particular event, that are stored in the GDACS database.  

GDACS developed routines to extract from each GTS message the reported Tsunami height, period and arrival time.  This allows therefore to visualize for each event which tide gauge was used by the Tsunami Service Providers during their analysis and if possible,  download and process these data.

Unfortunately not for all the events we have the GTS messages. GDACS started to collect them routiney since 2014 and with the help of some colleagues from NOA, Athens, we could include some data from 2012 to 2014. Also, in some cases the GTS mesages are not visible either because they are not open but protected by a passowrd (i.e. Australian Metereological Bureau) or because the processing of the GTS does not allow a secure understanding.

From the events that do not have GTS messages assciated,  we attempted to identify the gauges in teh area closeby the event (at a distance linearly increasing with magnitude). For these tide gauges, if the signals were available we processed with the Tsunami Detection model described in the pyTAD branch of this gitHub system and if we identified an 'alert' we marked that tide gauge useful for that particular event. With such methodology we could detect alerts in about half the events. Nevertheless, in some cases, the alert is not due to the tsunami wave but spurious spikes in the signals. This cannot be avoided and should require manual moderation that, for the moment was not done.

##Example oflist of events
![image](https://user-images.githubusercontent.com/10267112/193110688-b72dbb44-f395-4742-a388-67812352aee4.png)
The figure above shows the map of all the events from 2000 to current date.  The list shows the events separated by year. A filter allows to make a selection based on Minimum Magnitide or Minimum measured height (reported in the GTS messages (see above),  the starting/ending year of the list or the presence or absence of GTS message.

