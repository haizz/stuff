*Stuff* is very simple and primitive distributed storage for stuff (duh...)

Think of it as a remote key-value map (dict) with immutable items which
can replicate itself over a network of similar nodes.

Typical usage:

1. Start several nodes of stuff.
2. Introduce them to each other by making meet_neighbor call.
3. Put items (key, timestamp, value) to any node.
4. Item gets automatically replicated to all other nodes in the cluster.
5. Retrieve item by its key from any node.
6. ...
7. PROFIT

Item consists of:

1. Binary key -- could be UUID, for example.
2. timestamp
3. abstract binary data, no structure defined on DB level.

Stuff uses Apache Thrift for client-server and server-server communications.

See demo.py for an example.

Issues (in the name of simplicity):

1. No connection pooling in client.
2. Single-threaded server.
3. Non-optimal propagation of data through all cluster.
4. No conflict resolution.
5. Very primitive DB backend (dict from python).
6. No resync on node failure and recovery.
7. Very primitive, after all.
