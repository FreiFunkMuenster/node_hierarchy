from exceptions.HieraException import HieraException
from generator.Filter import Filter
from collections import OrderedDict
import json

class NodeProvisioningGen(object):
    def __init__(self, domains, args):
        self.__domains__ = domains
        self.__args__ = args
        self.__filter__ = Filter(self.__args__)
        self.__generatedDomains__ = self.__genDomains__()
        
    def __genDomains__(self):
        domains = {}
        for k,v in self.__domains__.items():
            domains[k] = self.__genDomain__(v)
        return domains
        
    def __genDomain__(self, domain):
        nodes = {}
        for localGraph in self.__filter__.filterLocalGraphs(domain, domain.localGraphs):
            try:
                for node in self.__filter__.filterNodes(domain, localGraph.getNodesWithNoDependencies()):
                    nodes[node.nodeID] = {
                        'hostname' : node.hostname,
                        'ipv6_addresses' : node.publicIPv6Addresses,
                        'domain_code' : node.domName 
                        }
            except HieraException:
                print('Was not able to add local cloud, because no VPN link was found.')

        return nodes
    
    def writeNodeProvisioningFile(self):
        f = open(self.__args__.out_file_node_provisioning,'w')
        f.write(self.__genNodeProvisioningFileContent__())
        f.close()
        print('Node Provisioning has been created. You can find it at:', self.__args__.out_file_node_provisioning)
        
    def __genNodeProvisioningFileContent__(self):
        entrys = {}
        for k, v in OrderedDict(sorted(self.__generatedDomains__.items())).items():
            for ksub, vsub in OrderedDict(sorted(v.items())).items():
                entrys[ksub] = {"target_domain": vsub["domain_code"]}
        return json.dumps(entrys, indent=4)
    
