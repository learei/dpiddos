import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from nfstream import NFStreamer, NFPlugin
import nfstream

time = None
count = 0


class LowDelta(NFPlugin):

    def on_init(self, pkt, flow):
        global count
        global time
        flow.expiration_id = 0
        flow.udps.exp = False
        if pkt.delta_time < 1:
            flow.udps.low_time_packets = 1
            count += 1
        else:
            flow.udps.low_time_packets = 0
        flow.udps.exp = False
        flow.udps.count = count

    def on_update(self, pkt, flow):
        global count
        global time
        if pkt.delta_time < 1:
            count += 1
            flow.udps.low_time_packets += 1

        flow.udps.exp = False
        flow.udps.count = count

        if count > 100:
            count = 0
            flow.udps.exp = True
            flow.expiration_id = -1 # -1 value force expiration

        if time is None:
            time = pkt.time
        time_diff = pkt.time - time

        if time_diff > 10000: #reset after 10s
            count = 0
            time = None


mssql_lowdelta = NFStreamer(source="wlp3s0",
                         udps=LowDelta(),
                         )

comparison_lowdelta = NFStreamer(source="wlp3s0",
                         udps=LowDelta())



#testing

a  = 0

for flow in mssql_lowdelta:
    print("In Class Counter: ",flow.udps.count)
    print("Packet count: ", flow.udps.low_time_packets)
    print("Expiration: ",flow.udps.test,"\n")
    if flow.udps.exp == True:
        a += 1

print("Number of Expirations mssql: ",a)

a  = 0

for flow in comparison_lowdelta:
    print("In Class Counter: ",flow.udps.count)
    print("Packet count: ", flow.udps.low_time_packets)
    print("Expiration: ",flow.udps.test,"\n")
    if flow.udps.exp == True:
        a += 1

print("Number of Expirations comp: ",a)

