# pyTAD
Python version of tad programme for IDSLs

The programmes in the prog folder represent the suite of programmes used in the Inexpensive Device for Sea Level Measurements ( IDSLs) devices and whose objective is to process the data in real time to provide an alert in case an anomalous wave, originated by a Tsunami or any other reason, is detected. 

The programme to be run on the IDSL can be launched with the command:

<code>
  python3 tad.py [ -c  <path of the configuration file>]
</code>

  
however for testing purposes, it is possible to use the scrape.py programme to read the sea level from available sea level repositories and get the quantities calculated on the fly.

To test the calculation procedure you can use the following command:
  
 Suppose that you have to analyse the tide gauge from the GLOSS Sea Level Facility,  you can use this command below, using as parameter  code  the value of the code from this list:
  https://www.ioc-sealevelmonitoring.org/list.php 
  
  If you want to analyse Algeciras, in Spain, the code is <b>alge</b>
  
  <code>
    scrape.py -code  alge  -n300 100  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode GLOSS  -out /temp/alge
  </code>
  
  where:
  
  -code :  is the code of the device,  as from the list indicated above<br>
  -n300 :  is the long term number of intervals<br>
  -30   :  is the short term number of intervals<br>
  -mult :  is the rms multiplication factor<br>
  -add  :  is the adding quantity to the rms<br>
  -th   :  is the threshold  to be overpassed<br>
  -mode :  is the indication of the type of sea level netwrok  (GLOSS/NOAA, BIG_INA...)  <br>
  -out  :  is optional and indicates where to write the output<br>
  
The output will be in the form of a list of data analysed applying the detection algorithm.  If the command is repeated, only the new data will be considered from the last time the command was run
