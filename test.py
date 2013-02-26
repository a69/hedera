#!/usr/bin/python


from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, CPULimitedHost
from mininet.net import Mininet

from FatTreeTopo import FatTreeTopo


from subprocess import Popen
from argparse import ArgumentParser

parser = ArgumentParser(description="ECMP routing")
parser.add_argument('-d', '--dir', dest='output_dir', default='/tmp',
        help='Output Directory')
parser.add_argument('-b', '--bw', dest='bw', type=int, default=100)

parser.add_argument('-p', '--cpu', dest='cpu', type=float, default=-1,
        help='cpu fraction to allocate to each host')
parser.add_argument('-q', '--queue', dest='queue', type=int, default=100,
        help='switch buffer size')

args = parser.parse_args()

def FatTreeNet(k=4, bw=100, cpu=-1, queue=100):
    
    Popen("~/pox/pox.py --no-cli ECMPController")

    host = custom(CPULimitedHost, cpu=cpu)
    link = custom(TCLink, bw=bw, max_queue_size=queue)
    topo = FatTreeTopo(k, speed=bw/1000)
    
    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=RemoteController)
    return net

def ECMPTest(args):
    k = 4
    bw = 100
    net = FatTreeNet( k=k, cpu=args.cpu, bw=bw, queue=args.queue)
    net.start()
    net.pingAll()

if __name__ == '__main__':
    ECMPTest(args)
    
