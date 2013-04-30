#!/usr/bin/env python

import os
import sys

STUFF_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(STUFF_DIR)

import time
from datetime import datetime

from stuff.stuff_service.ttypes import Item, NotFoundException

from stuff.client import StuffClientContext
from stuff.dummy_cluster import DummyCluster

def run_demo():
    # Start few nodes
    with DummyCluster() as cluster:
        cluster.start_node(9090)
        cluster.start_node(9091)
        cluster.start_node(9092)
        
        # Wait while nodes start (too lazy to implement proper sync)
        time.sleep(2)
    
        # Connect to the first node
        with StuffClientContext('localhost:9090') as node9090:
            # Is it alive?
            node9090.ping()
        
            # Introduce nodes in the cluster
            node9090.meet_neighbor('localhost:9091')
            node9090.meet_neighbor('localhost:9092')
        
            time.sleep(1)
        
            # Put some dummy item to the first node
            node9090.put(Item(key='42', timestamp=time.time(), data='data'))
    
        # Cool, now get the replicated data from the 3rd node
        with StuffClientContext('localhost:9092') as node9092:
            print node9092.get('42')
        
        # Start new node
        cluster.start_node(9093)
        time.sleep(1)
    
        with StuffClientContext('localhost:9093') as node9093:
            node9093.meet_neighbor('localhost:9090')
        
            # Wait for sync to complete
            time.sleep(1)
    
            # Now the data on node 9093 should be synced
            print node9093.get('42')
        
        # Test exceptions
        with StuffClientContext('localhost:9090') as node9090:
            try:
                print node9090.get('123')
            except NotFoundException, e:
                print e.msg
        
        # All tests done, shut down the cluster.
        cluster.terminate()
    
if __name__ == '__main__':
    run_demo()