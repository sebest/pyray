class Resource(object):
    """
    A resource representing a config object in the Stingray API
    """
    CONFIG_BASE = "/config"
    STATUS_BASE = "/status"
    POOLS_BASE = CONFIG_BASE + "/active/pools"

    def __init__(self, manager):
        self.manager = manager

    def poll_all_tms(self):
        """
        Query all the traffic manager children.

        :rtype: dict
        """
        method = "GET"
        resp, respbody = self.manager.time_request(
                                self.service_url + self.STATUS_BASE, method)

        # Strip out the local_tm
        for key, details in enumerate(respbody['children']):
            if details['name'] == 'local_tm':
                respbody['children'].pop(key)
        return respbody['children']