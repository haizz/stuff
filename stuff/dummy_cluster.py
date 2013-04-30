#!/usr/bin/env python
"""
Implementation of a primitive cluster consisting
of several nodes of stuff, each running in separate process.
"""

from stuff.node import StuffNodeSimpleServer

def start_server(port_number):
    StuffNodeSimpleServer('localhost', port_number).serve()

class DummyCluster(object):
    """Toy stuff cluster. Usage:
    
    with DummyCluster() as cluster:
        cluster.start_node(9090)
        cluster.start_node(9091)
        ...
    """
    def __init__(self):
        self.processes = []
        
    def start_node(self, port_number):
        """Start node of stuff listening on port_number."""
        from multiprocessing import Process
        process = Process(target=start_server, args=(port_number,))
        process.start()
        self.processes.append(process)
        
    def terminate(self):
        """Terminate all nodes in cluster"""
        processes = list(self.processes)
        for process in processes:
            process.terminate()
            self.processes.remove(process)
            
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.terminate()