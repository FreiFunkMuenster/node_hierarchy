from cloud.Graph import Graph
from shapely import MultiPoint
from exceptions.HieraException import HieraException
class LocalGraph(Graph):
    def __init__(self, nodes, links, debugPrint = False):
        super().__init__(nodes, links)
        self.__enableDebugPrinting__ = debugPrint
        if self.__enableDebugPrinting__:
            self.__debugPrint__()

    def getNodesWithVpn(self):
        nodes = []
        for link in self.__links__:
            if link.isVpn == True:
                nodes = nodes + [x for x in link.getEndpointNodes() if x not in nodes]
        return nodes
    
    def getCountOfNodesWithVpn(self):
        return len(self.getNodesWithVpn())
    
    def getDeptOfNode(self, node):
        return self.getDeptOfNodeByID(node.nodeID, [])
    
    def getDeptOfNodeByID(self, nodeID, trace):
        if self.getCountOfNodesWithVpn() == 0:
            raise HieraException('No VPN Node in LocalCloud was found!')
        new_trace = trace[:]
        new_trace.append(nodeID)
        lowestDepth = None
        currentDept = None
        links = self.getLinksByNodeID(nodeID)
        endpoints = []
        for link in links:
            endpoints = endpoints + [x for x in link.getEndpointNodeIDs() if x not in endpoints]
            if link.isVpn == True:
                return 0
        for childNodeID in endpoints:
            if childNodeID not in new_trace:
                currentDept = self.getDeptOfNodeByID(childNodeID, new_trace + endpoints)
                if currentDept != None:
                    currentDept = currentDept + 1
                    if lowestDepth == None or currentDept < lowestDepth:
                        lowestDepth = currentDept
        return lowestDepth
    
    def getMaxDepth(self):
        maxDepth = 0
        for k,v in self.__nodes__.items():
            nodeDepth = self.getDeptOfNode(v)
            maxDepth = nodeDepth if nodeDepth > maxDepth else maxDepth
        return maxDepth
    
    def getAllNodesWithDepthEquals(self, depth):
        nodes = []
        for k,v in self.__nodes__.items():
            if self.getDeptOfNode(v) == depth:
                nodes.append(v)
        return nodes
    
    def getNodesWithNoDependencies(self):
        nodesWithNoDependencies = []
        for k,v in self.__nodes__.items():
            depth = self.getDeptOfNode(v)
            hasDependencies = False
            for link in self.getLinksByNodeID(k):
                for node in link.getEndpointNodes():
                    if depth < self.getDeptOfNode(node):
                        hasDependencies = True
                        break
                if hasDependencies == True:
                    break
            else:
                nodesWithNoDependencies.append(v)
        return nodesWithNoDependencies
    
    def isAutoupdaterEnabledOnAllNodes(self):
        for k, v in self.__nodes__.items():
            if v.isAutoupdaterEnabled == False:
                return False
        return True
    
    def getLanLinksInCloud(self):
        links = []
        for link in self.__links__:
            if link.linkType == 'other' and link.isVpn == False:
                links.append(link)
        return links
    
    def areLanLinksInCloud(self):
        for link in self.__links__:
            if link.linkType == 'other' and link.isVpn == False:
                return True
        return False
    
    def getBranchesThatExistsInCloud(self):
        branches = []
        for k, v in self.__nodes__.items():
            if v.autoupdaterBranch not in branches:
                branches.append(v.autoupdaterBranch)
        return branches
    
    def getGeoCenterOfNodeCloud(self):
        geoPoints = []
        for k, v in self.__nodes__.items():
            if v.geo != None:
                geoPoints.append((v.geo['lon'], v.geo['lat']))
        return MultiPoint(geoPoints).representative_point()

    def __debugPrint__(self):
        print('nodes:')
        for k,v in self.__nodes__.items():
            print('>',v.hostname) 
        
        print('nodes with vpn:')
        for node in self.getNodesWithVpn():
            print('>',node.hostname)
        
        print('nodes with no dependencies:')
        for node in self.getNodesWithNoDependencies():
            print('>', node.hostname)
        
        print('maxdepth:', self.getMaxDepth())
        print('isAutoupdaterEnabledOnAllNodes:', self.isAutoupdaterEnabledOnAllNodes())
        print('areLanLinksInCloud:', self.areLanLinksInCloud())
        print('BranchesThatExistsInCloud:', self.getBranchesThatExistsInCloud())
        print('lan links in cloud:')
        for link in self.getLanLinksInCloud():
            hosts = link.getEndpointNodes()
            if len(hosts) == 1:
                print(' ', hosts.hostname, 'has unknown neighbour.')
            else:
                print(' ', hosts[0].hostname, '<--->', hosts[1].hostname)
        print('=====')
