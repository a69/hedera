# utility functions

from DCTopo import FatTreeTopo

from DCRouting import HashedRouting

TOPOS = {'ft': FatTreeTopo}
ROUTING = {'ECMP' : HashedRouting}


def buildTopo(topo):
    return FatTreeTopo(4)


def getRouting(routing, topo):
    return ROUTING[routing](topo)
