#/usr/bin/python

'''
Fat tree topology for data center networking

@author Milad Sharif (msharif@stanford.edu)

'''

from mininet.topo import Topo

class FatTreeTopo(Topo):
   
    super(FatTreeTopo, self).__init__()

    class FatTreeNode(object):
        def __init__(self, pod = 0, sw = 0, host = 0, dpid = None):
            ''' Create FatTreeNode '''
            if dpid:
                self.pod = ( dpid & 0xff0000 ) >> 16
                self.sw = ( dpid & 0xff00 ) >> 8
                self.host = ( dpid & 0xff )
                self.dpid = dpid
            else:
                self.pod = pod
                self.sw = sw
                self.host = host
                self.dpid = (pod << 16) + (sw << 8) + host 

        def name_str(self):
            ''' Return name '''
            return "%d_$d_%d" % (self.pod, self.sw, self.host)

        def name_str(self):
            ''' Return IP address '''
            return "10.%d.%d.%d" % (self.pod, self.sw, self.host)
    
    def __init__(self, k = 4, speed = 1.0):
        ''' Create FatTree topology 
            
            k : Number of pods (can support upto k^3/4 hosts)
            Speed : speed in Gbps
        '''

        pods = range(0, k)
        edge_sw = range(0, k/2)
        agg_sw = range(k/2, k)
        core_sw = range(0, k/2+1)
        hosts = range(2, k/2+2)

        for p in pods:
            for e in edge_sw:
                edge = FatTreeTopo.FatTreeNode(p,e,1)
                self.addSwitch(edge.name_str())

                for h in hosts:
                    host = FatTreeTopo.FatTreeNode(p,e,h)
                    self.addHost(host.name_str(), 'IP', host.ip_str())
                    self.addLink(edge,host)

                for a in agg_sw:
                    agg = FatTreeTopo.FatTreeNode(p,e,1)
                    self.addHost(agg.name_str())
                    self.addLink(agg,edge)
            
            for a in agg_sw:
                agg = FatTreeTopo.FatTreeNode(p,a,1)
                self.addSwitch(agg.name_str())

                for c in core_sw:
                    core = FatTreeTopo.FatTreeNode(k,a-k/2+1,c)
                    self.addSwitch(core.name_str())
                    self.addLink(agg,core)



