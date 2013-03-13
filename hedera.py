from mininet.topo import Topo
from mininet.node import Controller, RemoteController, OVSKernelSwitch, CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import custom
from mininet.log import setLogLevel, info, warn, error, debug

from DCTopo import FatTreeTopo, NonBlockingTopo
from DCRouting import Routing

from subprocess import Popen, PIPE
from argparse import ArgumentParser
import multiprocessing
from time import sleep
from monitor.monitor import monitor_devs_ng
import os
import sys


# Number of pods in Fat-Tree 
K = 4

# Queue Size
QUEUE_SIZE = 100

# Link capacity (Mbps)
BW = 10 

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

parser.add_argument('-n', '--nonblocking', dest='nonblocking', default=False,
        action='store_true', help='Run the experiment on the noneblocking topo')

args = parser.parse_args()

def NonBlockingNet(k=4, bw=10, cpu=-1, queue=100):
    ''' Create a NonBlocking Net '''

    topo = NonBlockingTopo(k)
    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)

    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=Controller)

    return net

def FatTreeNet(k=4, bw=10, cpu=-1, queue=100):
    ''' Create a Fat-Tree network '''

    pox_c = Popen("~/pox/pox.py DCController --topo=ft --routing=ECMP", shell=True)

    info('*** Creating the topology')
    topo = FatTreeTopo(k)

    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)
    
    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=RemoteController)

    return net

def trafficGen(args, hosts, net):
    ''' Run the traffic generator and monitor all of the interfaces '''
    listen_port = 12345
    sample_period_us = 1000000

    traffic_gen = 'cluster_loadgen/loadgen'
    if not os.path.isfile(traffic_gen):
        error('The traffic generator doesn\'t exist. \ncd hedera/cluster_loadgen; make\n')
        return

    info('*** Starting load-generators\n %s\n' % args.input_file)
    for h in hosts:
        tg_cmd = '%s -f %s -i %s -l %d -p %d 2&>1 > %s/%s.out &' % (traffic_gen,
                args.input_file, h.defaultIntf(), listen_port, sample_period_us,
                args.output_dir, h.name)
        h.cmd(tg_cmd)

    sleep(1)

    info('*** Triggering load-generators\n')
    for h in hosts:
        h.cmd('nc -nzv %s %d' % (h.IP(), listen_port))
    

    monitor = multiprocessing.Process(target = monitor_devs_ng, args =
        ('%s/rate.txt' % args.output_dir, 0.01))

    monitor.start()

    sleep(args.time)

    monitor.terminate()

    info('*** Stopping load-generators\n')
    for h in hosts:
        h.cmd('killall loadgen')

def ECMPTest(args):
    net = FatTreeNet( k=K, cpu=args.cpu, bw=BW, queue=QUEUE_SIZE)
    net.start()

    # wait for the switches to connect to the controller
    info('** Waiting for switches to connect to the controller\n')
    sleep(5)

    #net.pingAll()
 
    hosts = net.hosts
    trafficGen(args, hosts, net)

    net.stop()

def NonBlockingTest(args):
    net = NonBlockingNet(k=K, cpu=args.cpu, bw=BW, queue=QUEUE_SIZE)
    net.start()

    info('** Waiting for switches to connect to the controller\n')
    sleep(1)

    #net.pingAll()

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

    if args.nonblocking:
        NonBlockingTest(args)
    else:
        ECMPTest(args)

    clean()

    Popen("killall -9 top bwm-ng", shell=True).wait()
    os.system('sudo mn -c')
