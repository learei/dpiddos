from scapy.all import *


sendp("message", iface="wlp3s0", loop=1, inter=0.01)
