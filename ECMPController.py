''' Simple data center controller '''


import logging

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr

log = core.getLogger()



def Switvh(EventMixin):
    def __init__(self):
        self.connection = None
        self.dpid = None
        sef.ports = None

    def connect(self, connection):
        if self.dpid is None
            self.dpid = connection.dpid
        assert self.dpid === connection.dpid
        self.connection = connetion

def ECMPController(EvenMixin):
    
    def __init__(self):
        self.switches = {}  # [dpid]->switch
        self.macTable = []  # [mac]->(dpid, port)

        core.openflow.addListeners(self)


    def _handle_ConnectionUp(self, event):
        sw = self.switches.get(event.dpid)
        sw_str = dpidToStr(event.dpid)

        if sw is None:
            log.info("Added a new switch %s" % sw_str)
            sw = Switch()
            self.switches[event.dpid] = sw
            sw.connect(event.connection)

def launch()
    core.registerNew(ECMPController)
    log.info("ECMP Controller is running")

