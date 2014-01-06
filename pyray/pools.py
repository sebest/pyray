"""
Riverbed Stingray Pools
"""
from .base import Resource
from pyray import exceptions

class Pools(Resource):

    def all(self):
        """
        Retrieve a list of all configured pools.
        """
        method = "GET"
        resp, respbody = self.manager.time_request(self.POOLS_BASE, method)
        return [pool['name'] for pool in respbody['children']]

    def get(self, name):
        """
        Retrieve details for a given pool name

        :param name: A pool name
        :type name: str

        :rtype: dict
        """
        method = "GET"
        url = self.POOLS_BASE + "/{}".format(name)
        resp, respbody = self.manager.time_request(url, method)
        if respbody.has_key('error_id'):
            raise exceptions.ResourceNotFound('{} does not exist'.format(name))
        return Pool(self.manager, pool_name=name, details=respbody)

    def delete(self, name):
        """
        Delete a given pool

        :param name: A pool name
        :type name: str
        """
        method = 'DELETE'
        url = self.POOLS_BASE + "/{}".format(name)
        resp, respbody = self.manager.time_request(url, method)
        if resp.status_code is 204:
            return True
        else:
            raise exceptions.ResourceNotFound('{} does not exist'.format(name))

class Pool(Resource):

    def __init__(self, manager, pool_name, details):
        self.manager = manager
        self.pool_name = pool_name
        self.details = details

    def _validate_node(self, node, action):
        """
        Given a node, validate if it is a valid node in the pool

        :param nodes: A node to validate
        :type nodes: str
        """
        # Validate that node is draining
        if action == "undrain":
            if node not in self.draining_nodes:
                raise exceptions.ValidationError(
                        '{} is not draining'.format(node))
        # Validate that node is active and not already draining
        if action == "drain":
            if node not in self.nodes:
                raise exceptions.NodeNotInPool(
                        '{} is not in pool {}'.format(node, self.pool_name))
            elif node in self.draining_nodes:
                raise exceptions.ValidationError(
                        '{} is already draining'.format(node))
        if action == "add":
            if node in self.nodes:
                raise exceptions.NodeAlreadyExists(
                        '{} already exists in {}'.format(node, self.pool_name))
        if action == "remove":
            if node not in self.nodes:
                raise exceptions.NodeNotInPool(
                        '{} is not in pool {}'.format(node, self.pool_name))

    @property
    def draining_nodes(self):
        """
        Return a list of nodes draining
        """
        return self.details['properties']['basic']['draining']

    @property
    def nodes(self):
        """
        Return a list of nodes in the pool
        """
        return self.details['properties']['basic']['nodes']

    def drain_nodes(self, nodes=[]):
        """
        Given a list of nodes, put them in 'draining' status

        :param nodes: A list of nodes to drain
        :type nodes: list
        """
        method = "PUT"
        url = self.POOLS_BASE + "/{}".format(self.pool_name)
        for node in nodes:
            self._validate_node(node, action='drain')
            self.details['properties']['basic']['draining'].append(node)

        # Send the updated config to the LB
        resp, respbody =  self.manager.time_request(url,
                                                    method,
                                                    data=self.details)
        # Validate response
        if resp.status_code is not 200:
            error = respbody['error_info']['basic']['draining']['error_text']
            raise exceptions.ValidationError('Drain Error: {}'.format(error))
        else:
            return respbody

    def undrain_nodes(self, nodes=[]):
        """
        Given a list of nodes, put them in 'active' status

        :param nodes: A list of nodes to activate
        :type nodes: list
        """
        method = "PUT"
        url = self.POOLS_BASE + "/{}".format(self.pool_name)
        for node in nodes:
            self._validate_node(node, action='undrain')
            self.details['properties']['basic']['draining'].remove(node)

        # Send the updated config to the LB
        return self.manager.time_request(url,
                                         method,
                                         data=self.details)

    def node_details(self):
        """
        Return all the nodes in the pool with their details.
        """
        method = "GET"
        nodes = {}
        tms_children = self.poll_all_tms()
        # Get all of our pools and nodes
        for tm in tms_children:
            per_pool_node_url = tm['href'] + 'statistics/nodes/per_pool_node/'
            resp, respbody = self.manager.time_request(per_pool_node_url, method)
            pools_to_nodes = [entry for entry in respbody['children']]

        for node in pools_to_nodes:
            if self.pool_name in node['href']:
                resp, respbody = self.manager.time_request(node['href'], method)
                nodes[node['name']] = respbody
        return nodes

    def add_node(self, address, port):
        """
        Add a node to the pool. Return the new pool configuration dictionary.

        Note: Node is added to the pool in a state of 'Active'

        :param address: IP Address of the backend node
        :type address: str
        :param port: Service port for the backend node. IE: 80 or 443
        :type port: int
        :rtype: dict
        """
        method = "PUT"
        node = "{address}:{port}".format(address=address, port=port)
        url = self.POOLS_BASE + "/{}".format(self.pool_name)
        self._validate_node(node, action='add')
        self.details['properties']['basic']['nodes'].append(node)
        resp, respbody = self.manager.time_request(url,
                                                   method,
                                                   data=self.details)

        if resp.status_code is not 200:
            error = respbody['error_info']['basic']['nodes']['error_text']
            raise exceptions.ValidationError('Add node error: {}'.format(error))
        else:
            return respbody

    def remove_node(self, address, port):
        """
        Remove a node to the pool. Return the new pool configuration dictionary.

        :param address: IP Address of the backend node
        :type address: str
        :param port: Service port for the backend node. IE: 80 or 443
        :type port: int
        :rtype: dict
        """
        method = "PUT"
        node = "{address}:{port}".format(address=address, port=port)
        url = self.POOLS_BASE + "/{}".format(self.pool_name)
        self._validate_node(node, action='remove')
        self.details['properties']['basic']['nodes'].remove(node)
        resp, respbody = self.manager.time_request(url,
                                                   method,
                                                   data=self.details)

        if resp.status_code is not 200:
            error = respbody['error_info']['basic']['nodes']['error_text']
            raise exceptions.ValidationError('Remove node error: {}'.format(error))
        else:
            return respbody
