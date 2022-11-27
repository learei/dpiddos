import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from nfstream import NFStreamer, NFPlugin
import nfstream

time = None
lowflow = 0
freq_alarm = 0


class Frequency(NFPlugin):
    def on_init(self, pkt, flow):
        global lowflow
        global time
        global freq_alarm
        flow.expiration_id = 0
        flow.udps.fr_alarm = False
        if flow.bidirectional_duration_ms == 0:
            bidir = 0.0001
        else:
            bidir = flow.bidirectional_duration_ms
        frequency = flow.bidirectional_packets/bidir

        if frequency > 300:
            freq_alarm += 1
            time = None

    def on_update(self, pkt, flow):
        global lowflow
        global time
        global freq_alarm
        if flow.bidirectional_duration_ms == 0:
            bidir = 0.0001
        else:
            bidir = flow.bidirectional_duration_ms
        frequency = flow.bidirectional_packets/bidir

        if frequency > 300:
            freq_alarm += 1
            flow.udps.fr_alarm = True
            time = None

        if time is None:
            time = pkt.time
        time_diff = pkt.time - time

        if time_diff > 10000:
            freq_alarm = 0
            time = None




mssql_freq = NFStreamer(source="wlp3s0",
                         udps=Frequency(),
                         )

comparison_frequency = NFStreamer(source="wlp3s0",
                         udps=Frequency())



#testing

a  = 0

for flow in mssql_freq:
   if flow.udps.fr_alarm == True:
        a += 1

print("Number of Expirations mssql: ",a)

a  = 0

for flow in comparison_frequency:
   if flow.udps.fr_alarm == True:
        a += 1
        print("LowFlow: ",lowflow)
        print("Expiration: ",flow.udps.fr_alarm,"\n")

print("Number of Expirations comp: ",a)

