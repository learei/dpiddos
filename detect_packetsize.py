import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from nfstream import NFStreamer, NFPlugin
import nfstream

time = None
lowflow = 0


class PacketSizePerFlow(NFPlugin):
    def on_init(self, pkt, flow):
        global lowflow
        global time
        flow.expiration_id = 0
        flow.udps.packet_count = 1
        lowflow += 1
        flow.udps.is_subtracted = False
        flow.udps.alarm = False
        flow.udps.lowflow = lowflow
        if time is None:
            time = pkt.time

    def on_update(self, pkt, flow):
        global lowflow
        global time

        flow.udps.lowflow = lowflow
        flow.udps.packet_count = 1

        if flow.udps.packet_count > 4 and not flow.is_subtracted:
            lowflow -= 1
            flow.udps.is_subtracted = True



        if lowflow > 100:
            flow.udps.expiration_id = -1 # -1 value force expiration
            flow.udps.alarm = True
            lowflow = 0
            time = None

        if time is None:
            time = pkt.time
        time_diff = pkt.time - time

        if time_diff > 10000:
            lowflow = 0
            time = None



mssql_packetsize_pf = NFStreamer(source="wlp3s0",
                         udps=PacketSizePerFlow(),
                         )

comparison_packetsize_pf = NFStreamer(source="wlp3s0",
                         udps=PacketSizePerFlow())


#testing
a = 0

for flow in mssql_packetsize_pf:
   if flow.udps.alarm == True:
        a += 1

print("Number of Expirations mssql: ",a)


a = 0

for flow in comparison_packetsize_pf:
   if flow.udps.alarm == True:
        a += 1

print("Number of Expirations comp: ",a)
