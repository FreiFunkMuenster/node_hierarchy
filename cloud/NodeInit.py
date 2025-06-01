class NodeInit(object):
    def __init__(self, NodeJsonObject):
        self.__jsonObject__ = NodeJsonObject
        self.nodeID = self.__jsonObject__['nodeinfo']['node_id']
        self.interfaces = self.__getInterfaces__()
        self.hostname = self.__jsonObject__['nodeinfo']['hostname']
        self.isGateway = self.__jsonObject__['nodeinfo']['isGateway']
        self.geo = self.__getGeo__()
        self.isAutoupdaterEnabled = self.__getAutoupdaterStatus__()
        self.autoupdaterBranch = self.__getBranch__()
        self.isOnline = self.__jsonObject__['nodeinfo']['isOnline']
        self.publicIPv6Addresses = self.__getPublicAddresses__()
        self.domName = self.__getDomainCode__() or self.__getSiteCode__()

    def __getInterfaces__(self):
        try:
            return self.__jsonObject__['nodeinfo']['network']['mesh']['bat0']['interfaces']
        except:
            return {}

    def __getAutoupdaterStatus__(self):
        try:
            return self.__jsonObject__['nodeinfo']['software']['autoupdater']['enabled']
        except:
            return False

    def __getBranch__(self):
        try:
            return self.__jsonObject__['nodeinfo']['software']['autoupdater']['branch']
        except:
            return None

    def __getGeo__(self):
        try:
            return {
                'lat' : self.__jsonObject__['nodeinfo']['location']['latitude'],
                'lon' : self.__jsonObject__['nodeinfo']['location']['longitude']
            }
        except:
            return None

    def __getPublicAddresses__(self):
        addresses = []
        try:
            for address in self.__jsonObject__['nodeinfo']['network']['addresses']:
                if not address.startswith('fe80'):
                    addresses.append(address)
        except:
            pass
        return addresses
    
    def __getSiteCode__(self):
        try:
            return self.__jsonObject__['nodeinfo']['system']['site_code']
        except:
            return None

    def __getDomainCode__(self):
        try:
            return self.__jsonObject__['nodeinfo']['system']['domain_code']
        except:
            return None
