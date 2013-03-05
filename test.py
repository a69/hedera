#!/usr/bin/python


from mininet.topo import Topo
from mininet.node import Controller, RemoteController, OVSKernelSwitch, CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import custom
from mininet.log import setLogLevel, info, warn, error, debug

from DCTopo import FatTreeTopo, NonBlockingTopo

from subprocess import Popen, PIPE
from argparse import ArgumentParser

from time import sleep
import os
import sys

parser = ArgumentParser(description="ECMP routing")
parser.add_argument('-d', '--dir', dest='output_dir', default='/tmp',
        help='Output Directory')
parser.add_argument('-b', '--bw', dest='bw', type=int, default=100)

parser.add_argument('-p', '--cpu', dest='cpu', type=float, default=-1,
        help='cpu fraction to allocate to each host')
parser.add_argument('-q', '--queue', dest='queue', type=int, default=100,
        help='switch buffer size')

args = parser.parse_args()

def NonBlockingNet(k=4, bw=100, cpu=-1, queue=100):
    ''' Create a NonBlocking Net ''' 
    
    topo = NonBlockingTopo(k)
    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)

    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=Controller)
    return net

def FatTreeNet(k=4, bw=100, cpu=-1, queue=100):
    ''' Create a Fat-Tree network '''

    pox_c = Popen("~/pox/pox.py ECMPController --topo=ft", shell=True)
    #topo = NonBlockingTopo(k)
    topo = FatTreeTopo(k, speed=bw/1000)
    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)
    
    print "** Created the Topo"

    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=RemoteController)

    return net

def ECMPTest(args):
    k = 4
    bw = 100
    net = FatTreeNet( k=k, cpu=args.cpu, bw=bw, queue=args.queue)
    
    print "** Createid the Network"
    
    # wait for the switches to connect to the controller
    info('** Waiting for switches to connect to the controller\n')
    sleep(5)
    
    net.start()
    print "** Start Pinging"
    net.pingPair() 

def NonBlockingTest(args):
    k = 4
    bw = 100
    net = NonBlockingNet(k=k, cpu=args.cpu, bw=bw, queue=args.queue)    
    net.start()
    net.pingAll()

def clean():
    ''' Clean any the running instances of POX '''

    p = Popen("ps aux | grep 'pox' | awk '{print $2}'",
            stdout=PIPE, shell=True)
    p.wait()
    procs = (p.communicate()[0]).split('\n')
    for pid in procs:
        try:
            pid = int(pid)
            Popen('kill %d' % pid, shell=True).wait()
        except:
            pass

if __name__ == '__main__':
    
    clean()
    #NonBlockingTest(args)
    ECMPTest(args)

    os.system('sudo mn -c') 
