#!/usr/bin/python


from mininet.topo import Topo
from mininet.node import Controller, RemoteController, OVSKernelSwitch, CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import custom
from mininet.log import setLogLevel, info, warn, error, debug

from DCTopo import FatTreeTopo, NonBlockingTopo
from routing import HashedRouting

from subprocess import Popen, PIPE
from argparse import ArgumentParser
import multiprocessing
from time import sleep
from monitor.monitor import monitor_devs_ng
import os
import sys

parser = ArgumentParser(description="ECMP routing")

parser.add_argument('-d', '--dir', dest='output_dir', default='log',
        help='Output directory')

parser.add_argument('-i', '--input', dest='input_file',
        default='inputs/all_to_all_data',
        help='Traffic generator input file')

parser.add_argument('-t', '--time', dest='time', type=int, default=30,
        help='Duration (sec) to run the experiment')

parser.add_argument('-p', '--cpu', dest='cpu', type=float, default=-1,
        help='cpu fraction to allocate to each host')

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
    
    info('** Creating the topology')
    topo = FatTreeTopo(k, speed=bw/1000)
    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)
    
    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=RemoteController)

    return net

def trafficGen(args, hosts, net):
    ''' '''
    listen_port = 12345
    sample_period_us = 1000000

    traffic_gen = 'cluster_loadgen/loadgen'
    if not os.path.isfile(traffic_gen):
        error('The traffic generator doesn\'t exist. \ncd \
                hedera/cluster_loadgen; make')
        return

    info('** Starting load-generators\n')
    for h in hosts:
        tg_cmd = '%s -f %s -i %s -l %d -p %d 2&>1 > %s/%s.out &' % (traffic_gen,
                args.input_file, h.defaultIntf(), listen_port, sample_period_us,
                args.output_dir, h.name)
        h.cmd(tg_cmd)
   
    print h.defaultIntf()
    print args.input_file
    print listen_port
    print sample_period_us
    
    sleep(1)

    info('** Triggering load-generators\n')
    for h in hosts:
        h.cmd('nc -nzv %s %d' % (h.IP(), listen_port))


    monitor = multiprocessing.Process(target = monitor_devs_ng, args =
        ('%s/rate.txt' % args.output_dir, 0.01))
    
    monitor.start()

    #sleep(args.time)
    sleep(5)

    monitor.terminate()

    info('** Stopping load-generators\n')
    for h in hosts:
        h.cmd('killall loadgen')

def ECMPTest(args):
    k = 4
    bw = 100
    queue = 100
    net = FatTreeNet( k=k, cpu=args.cpu, bw=bw, queue=queue)
    
    # wait for the switches to connect to the controller
    info('** Waiting for switches to connect to the controller\n')
    sleep(5)
    
    net.start()
    print "** Start Pinging"
    net.pingPair() 
    net.stop()

def NonBlockingTest(args):
    k = 4
    bw = 100
    queue = 100
    net = NonBlockingNet(k=k, cpu=args.cpu, bw=bw, queue=queue)    
    net.start()
    
    info('** Waiting for switches to connect to the controller\n')
    sleep(1)

    net.pingAll()

    hosts = net.hosts


    trafficGen(args, hosts, net)

    net.stop()

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
    
    setLogLevel( 'info' )
    if not os.path.exists(args.output_dir):
        print args.output_dir
        os.makedirs(args.output_dir)

    clean()
    
    NonBlockingTest(args)
    #ECMPTest(args)

    clean()

    os.system('sudo mn -c') 
