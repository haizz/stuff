#!/usr/bin/env python
"""
Definitions of the server side of stuff.
"""

import sys

from stuff.client import StuffClientContext

import logging
logging.basicConfig(format='%(asctime)s\t%(name)-15s%(levelname)s\t%(message)s', 
                    stream=sys.stderr,
                    level=logging.DEBUG)

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from stuff.stuff_service import StuffStorage
from stuff.stuff_service.ttypes import *

class StuffHandler(object):
    """Handler of all requests for stuff"""
    def __init__(self, hostname, port_number):
        """Construct stuff handler object."""
        self.logger = logging.getLogger('Stuff%d' % port_number)
        self.hostname = hostname
        self.port_number = port_number
        self.stuff_db = dict()
        self.neighbors = set()
        
    def ping(self):
        """Check if the node is alive"""
        self.logger.info('Ping')
        
    def put(self, item):
        """Put item to the DB"""
        self.sync_put(item, [self.address])
        
    def get(self, key):
        """Retrieve item from the DB by its key.
        Throw NotFoundException if the key is not found."""
        self.logger.info(u'Getting item with key %s' % unicode(key))
        if not key in self.stuff_db:
            raise NotFoundException, u'Key %s was not found' % key
        return self.stuff_db[key]
                
    def meet_neighbor(self, address):
        """Add address to the list of neighbors, retrieve new data and
        introduce myself to the new neighbor."""
        if address == self.address:
            return
        if address not in self.neighbors:
            self.logger.info('Adding neighbor %s' % address)
            try:
                with StuffClientContext(address) as neighbor:
                    # Get new items from the neighbor
                    new_items = neighbor.sync_get(self.get_latest_timestamp())
                    self.stuff_db.update(dict((i.key, i) for i in new_items))
                    # Introduce myself
                    neighbor.meet_neighbor(self.address)
            except Exception, ex:
                # Neighbor doesn't work
                logger.exception(ex)
            else:
                self.neighbors.add(address)
                
    def sync_put(self, item, propagation_trace):
        """Sync the item through all neighbors.
        propagation_trace is the list of all visited addresses so far."""
        key = item.key
        if key not in self.stuff_db:
            self.logger.info(u'Putting item with key %s' % unicode(key))
            self.stuff_db[item.key] = item
            self._propagate(lambda c, pt: c.sync_put(item, pt),
                            propagation_trace)

    def sync_get(self, latest_timestamp):
        """Retrieve all items newer that latest_timestamp"""
        return [i for i in self.stuff_db.itervalues() if i.timestamp > latest_timestamp]
    
    @property
    def address(self):
        """Return the node address in string format"""
        return '%s:%s' % (self.hostname, self.port_number)
        
    def get_latest_timestamp(self):
        """Return the timestamp of newest item in DB"""
        if not self.stuff_db:
            return 0
        return max(i.timestamp for i in self.stuff_db.itervalues())
            
    def _propagate(self, callable, propagation_trace):
        """Go through all neighbors and call callable(address, propagation_trace + [self.address]).
        propagation_trace keeps the list of visited addresses so far."""
        neighbors = list(self.neighbors)
        for address in neighbors:
            # Don't visit already visited addresses
            if address not in propagation_trace:
                with StuffClientContext(address) as neighbor:
                    self.logger.info('Syncing to %s', address)
                    try:
                        callable(neighbor, propagation_trace + [address])
                    except TTransport.TTransportException, ex:
                        # Remove neighbor in case of network error
                        logger.exception(ex)
                        self.neighbors.remove(address)
                    
class StuffNodeSimpleServer(object):
    """Simple server to serve requests for stuff. Usage:
    
    >>> StuffNodeSimpleServer("localhost", 9090).serve()
    """
    def __init__(self, hostname, port_number):
        self.hostname = hostname
        self.port_number = port_number
        self.handler = StuffHandler(hostname, port_number)
        self.processor = StuffStorage.Processor(self.handler)
        self.transport = TSocket.TServerSocket(port=port_number)
        self.tfactory = TTransport.TBufferedTransportFactory()
        self.pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        self.server = TServer.TSimpleServer(self.processor, self.transport, self.tfactory, self.pfactory)
        
    def serve(self):
        """Start the server."""
        logging.info('Starting node for stuff at port %s... Press Ctrl-C to stop.', self.port_number)
        self.server.serve()
        
if __name__ == '__main__':
    StuffNodeSimpleServer('localhost', 9090).serve()

__all__ = ['StuffNodeSimpleServer']

