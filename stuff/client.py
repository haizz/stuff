#!/usr/bin/env python

"""Client side of stuff"""

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from stuff.stuff_service import StuffStorage
from stuff.stuff_service.ttypes import *

class StuffClientContext(object):
    """Wrapper of thrift socket transport & client objects. Usage:
    
    with StuffClientContext("localhost:9090") as client:
        client.ping()
    """
    def __init__(self, address):
        """Initialize client transport. address should be in hostname:port format."""
        hostname, port_number = address.split(':')
        port_number = int(port_number)
        transport = TSocket.TSocket(hostname, port_number)
        self.transport = TTransport.TBufferedTransport(transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = StuffStorage.Client(self.protocol)
        
    def __enter__(self):
        """Open transport"""
        self.transport.open()
        return self.client
        
    def __exit__(self, *args):
        """Close transport"""
        self.transport.close()

        
        
