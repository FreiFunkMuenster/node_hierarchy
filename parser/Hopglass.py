from parser.JsonParser import JsonParser
import collections
import json
import datetime
from datetime import timedelta, timezone

class Hopglass(JsonParser):
    def __init__(self, args):
        super().__init__(args.raw_json)
        self.ifIDs = {}
        self.links = collections.defaultdict(dict)
        self.nodes = {}
        self.gatewayMacs = []
        self.gateways = []
        self.offlineThreshold = args.offline_threshold
        self.__aggregateData__()
        # print(self.ifIDs)
        # for k, v in self.links.items():
        #     print(k,v,'\n')
        
    def __aggregateData__(self):
        for nodeID, nodeData in self.__jsonData__.items():

            # let pass nodes that provide all required informations only
            if not set(('nodeinfo', 'neighbours', 'statistics')) <= set(nodeData):
                continue

            nodeInfo = nodeData['nodeinfo']
            neighbours = nodeData['neighbours']
            statistics = nodeData['statistics']

            if not 'batadv' in neighbours:
                continue

            if not 'mesh' in nodeInfo.get('network', {}):
                continue

            if statistics.get('gateway', False):
                self.gatewayMacs.append(statistics['gateway'])

            for batID, batVal in nodeInfo['network']['mesh'].items():
                if not 'interfaces' in batVal:
                    continue
                for ifType, ifVal in batVal['interfaces'].items():
                    for mac in ifVal:
                        self.ifIDs[mac] = {
                                'type' : ifType,
                                'nodeID' : nodeID
                            }

            self.nodes[nodeID] = nodeData

        for nodeID, nodeData in self.nodes.items():
            nodeData['nodeinfo']['isGateway'] = False
            nodeLastSeen = datetime.datetime.strptime(nodeData['lastseen'],'%Y-%m-%dT%H:%M:%S.%fZ')
            if (datetime.datetime.utcnow()-nodeLastSeen).seconds/60 > self.offlineThreshold:
                nodeData['nodeinfo']['isOnline'] = False
                continue
            else:
                nodeData['nodeinfo']['isOnline'] = True
            for iname, ivalue in nodeData['neighbours']['batadv'].items():
                if 'neighbours' not in ivalue:
                    continue
                if iname in self.gatewayMacs:
                    nodeData['nodeinfo']['isGateway'] = True
                if not iname in self.ifIDs:
                    continue
                for nname, nvalue in ivalue['neighbours'].items():
                    if nname not in self.ifIDs:
                        continue
                    nifID = self.ifIDs[nname]['nodeID']
                    partID = (nodeID, nifID) if nodeID > nifID else (nifID, nodeID)
                    linkID = (iname, nname) if iname > nname else (nname, iname)

                    linkNode =  {
                                    'nodeID' : nodeID,
                                    'type' : self.ifIDs[iname]['type'],
                                    'tq' : nvalue['tq']
                                }

                    if linkID in self.links[partID]:
                        self.links[partID][linkID].append(linkNode)
                    else:
                        self.links[partID][linkID] = [linkNode]
    
    
    def getLinksForNodeID(self, nodeID):
        links = []
        for link in self.links:
            if link['target']['node_id'] == nodeID or link['source']['node_id'] == nodeID:
                links.append(link)
        return links
