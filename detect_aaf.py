import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from nfstream import NFStreamer, NFPlugin
import nfstream

lowaaf = 0
time = None

class AAF(NFPlugin):

    def on_init(self, pkt, flow):
        global lowaaf
        global time
        flow.expiration_id = 0
        flow.udps.aaf = 0
        if pkt.direction == 0:
                flow.udps.src2dst_size = pkt.payload_size
                flow.udps.dst2src_size = 0
        elif pkt.direction == 1:
                flow.udps.src2dst_size = 0
                flow.udps.dst2src_size = pkt.payload_size
        flow.udps.alarm = False
        flow.udps.lowaaf = lowaaf
        if time is None:
            time = pkt.time


    def on_update(self, pkt, flow):
        global lowaaf
        global time


        if pkt.direction == 0:
            flow.udps.src2dst_size += pkt.payload_size
        elif pkt.direction == 1:
            flow.udps.dst2src_size += pkt.payload_size

        flow.udps.lowaaf = lowaaf
        if flow.udps.src2dst_size != 0 and flow.udps.dst2src_size != 0:
            flow.udps.aaf = flow.udps.dst2src_size/flow.udps.src2dst_size

        if flow.udps.aaf != 0 and flow.udps.aaf < 0.1:
            lowaaf += 1



        if lowaaf > 100:
            flow.udps.expiration_id = -1 # -1 value force expiration
            flow.udps.alarm = True
            lowaaf = 0
            time = None

        if time is None:
            time = pkt.time
        time_diff = pkt.time - time

        if time_diff > 10000:
            lowaaf = 0
            time = None



mssql_aaf = NFStreamer(source="wlp3s0",
                         udps=AAF(),
                         )

comp_aaf = NFStreamer(source="wlp3s0",
                         udps=[AAF()])



a = 0


for flow in mssql_aaf:
   if flow.udps.alarm == True:
        a += 1


print("Number of Expirations mssql: ",a)


a = 0

for flow in comp_aaf:
   if flow.udps.alarm == True:
        a += 1


print("Number of Expirations comp: ",a)
