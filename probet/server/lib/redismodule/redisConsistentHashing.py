import hashlib

class HashRing(object):
    def __init__(self, nodes=None, replicas=3):
        """
        Manages a hash ring
        :nodes 
            a list of object that have a proper __str__ representation
        :replicas
            indicates how many virtual points should be used per node,
            replicas are required to improve the distribution
        """

        self.replicas = replicas
        self.ring = {}
        self._sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node):
        """
        Adds a node to the hash ring(including a number of replicas)
        """
        for i in range(0, self.replicas):
            key = self.gen_key("%s:%s" % (node, i))
            self.ring[key] = node
            self._sorted_keys.append(key)

        self._sorted_keys.sort()

    def remove_node(self, node):
        """
        Removes node from the hash ring and its replicas
        """
        for i in range(0, self.replicas):
            key = self.gen_key("%s:%s" % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)

    def get_node_keys(self, node):
        """
        Given a node return all its virturl node keys
        """
        keys = []
        for i in range(0, self.replicas):
            key = self.gen_key("%s:%s" % (node, i))
            keys.append(key)
        return keys

    def get_node(self, string_key):
        """
        Given a string key corresponding node in the hash ring is returned.
        If the hash ring is empty, None is returned.
        """
        return self.get_node_pos(string_key)[0]

    def get_node_pos(self, string_key):
        """
        Given a string key corresponding node in the hash ring is returned
        along with it's position in the ring.

        If the hash ring is empty, (None, None) is returned
        """
        if not self.ring:
            return None, None

        key = self.gen_key(string_key)
        nodes = self._sorted_keys
        for i in range(0, len(nodes)):
            node = nodes[i]
            if key <= node:
                return self.ring[node], i

        return self.ring[nodes[0]], 0

    def get_nodes(self, string_key):
        """
        Given a string key it returns the nodes as a generator that can hold the key.
        The generator is never ending and iterates through the ring starting at the correct position.
        """
        if not self.ring:
            yield None

        node, pos = self.get_node_pos(string_key)
        for key in self._sorted_keys:
            yield self.ring[key]

    def gen_key(self, key:str):
        """
        Given a string key it return a long value,
        this long value represent a place on the hash ring.

        md5 is currently used because it mixes well.
        """

        m = hashlib.md5.new()
        m.update(key.encode())
        return int(m.hexdigest(),16)