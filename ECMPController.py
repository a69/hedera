''' Simple data center controller '''


import logging

import sys
sys.path.append('/home/ubuntu/hedera/')

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr

from util import buildTopo


log = core.getLogger()


class Switch(EventMixin):
    def __init__(self):
        self.connection = None
        self.dpid = None
        self.ports = None

    def connect(self, connection):
        if self.dpid is None:
            self.dpid = connection.dpid
        assert self.dpid == connection.dpid
        self.connection = connection

class ECMPController(EventMixin):
    def __init__(self, t):
        self.switches = {}  # [dpid]->switch
        self.macTable = {}  # [mac]->(dpid, port)
        self.t = t          # Topo object
        self.all_switches_up = False
        core.openflow.addListeners(self)

    def _handle_PacketIn(self, event):
        #log.info("Got a new packet")
        pass

    def _handle_ConnectionUp(self, event):
        sw = self.switches.get(event.dpid)
        sw_str = dpidToStr(event.dpid)
        sw_name = self.t.node_gen(dpid = event.dpid).name_str()
        
        #log.info("A new switch came up: %s", sw_str)
        if sw is None:
            log.info("Added a new switch %s" % sw_name)
            sw = Switch()
            self.switches[event.dpid] = sw
            sw.connect(event.connection)

        if len(self.switches)==len(self.t.switches()):
            log.info("All of the switches are up")

def launch(topo = None):
    print topo
    if not topo:
        raise Exception ("Please specify the topology")
    else: 
        t = buildTopo(topo)

    core.registerNew(ECMPController, t)
    log.info("** ECMP Controller is running")

