#!/usr/bin/env python
import argparse
# from parser.NodesParser import NodesParser
# from parser.GraphParser import GraphParser
from parser.Hopglass import Hopglass
from cloud.Node import Node
from cloud.Link import Link
from cloud.GlobalGraph import GlobalGraph
from parser.ShapesParser import ShapesParser
from cloud.Domaene import Domaene
from generator.NginxConfGen import NginxConfGen
from generator.NodeProvisioning import NodeProvisioningGen
from info.Info import Info

class NodeHierarchy(object):
    def __init__(self):
        self.__args__ = self.__parseArguments__()
        self.__hopglass = Hopglass(self.__args__)
        # self.__nodesJson__ = NodesParser(self.__args__.json_path)
        # self.__graphJson__ = GraphParser(self.__args__.json_path)
        self.__shapesJson__ = self.__parseShapes__()
        self.nodes = self.__createNodeObjects__()
        self.links = self.__createLinkObjects__()
        self.globalGraph = self.__createGlobalGraph__()
        self.domains = self.__createDomains__()
        self.nginxConf = NginxConfGen(self.domains, self.__args__)
        self.nginxConf.writeNginxConfigFile()
        self.nodeProv = NodeProvisioningGen(self.domains, self.__args__)
        self.nodeProv.writeNodeProvisioningFile()
        self.infos = Info(self.__args__.info, self.__args__.info_out_path, self.__args__.info_out_type, self.__args__.info_filters, self.nodes, self.globalGraph, self.domains)

    def __parseShapes__(self):
        shapesJson = {}
        for targetName in self.__args__.targets:
            shapesJson[targetName] = ShapesParser(self.__args__.shapes_path, targetName)
        return shapesJson

    def __createDomains__(self):
        domains = {}
        for k, v in self.__shapesJson__.items():
            print('Create Domain object #',len(domains), '\r',end = '')
            domains[k] = Domaene(k,v, self.globalGraph)
        print('')
        return domains

    def __createNodeObjects__(self):
        nodes = {}
        for nodeID, nodeValue in self.__hopglass.nodes.items():
            if nodeValue['nodeinfo']['node_id']:
                print('Create Node object #',len(nodes), '\r',end = '')
                nodes[nodeID] = Node(self.__prepareNodeData__(nodeValue))
        print('')
        return nodes

    def __prepareNodeData__(self, nodeValue):
        if self.__args__.site_to_target_prefix:
            pref = self.__args__.site_to_target_prefix.split(',')
            try:
                nodeValue['nodeinfo']['system']['site_code'] = nodeValue['nodeinfo']['system']['site_code'].replace(pref[0],pref[1])
            except:
                pass
        return nodeValue

    def __createLinkObjects__(self):
        links = []
        for linkParID, linkPar in self.__hopglass.links.items():
            for linkID, link in linkPar.items():
                print('Create Link object #',len(links), '\r',end = '')
                if linkParID[0] != 'null' and linkParID[1] != 'null':
                    links.append(Link(link, (self.nodes[linkParID[0]], self.nodes[linkParID[1]])))
        print('')
        return links
            
    def __createGlobalGraph__(self):
        return GlobalGraph(self.nodes, self.links, self.__args__.debug)

    def __parseArguments__(self):
        parser = argparse.ArgumentParser(description='This Script generates a hierarchical nodes list for node migration using nginx geo feature.')
        parser.add_argument('-r', '--raw-json', required=False, default='https://karte.freifunk-muensterland.de/data/raw.json', help='Location of raw.json file (can be local folder or remote URL).')
        parser.add_argument('-s', '--shapes-path', required=False, default='https://domaenenwahl.ffmsl.de/shapes/', help='Path of shapefiles (can be local folder or remote URL).')
        parser.add_argument('-t', '--targets', nargs='+', required=True, help='List of targets which should be proceeded. Example: -t citya cityb ...')
        parser.add_argument('-sttp', '--site-to-target-prefix', required=False, help='Used to match site and target also when prefixes are different. Example: -sttp "ffmsd,domaene"')
        parser.add_argument('-o', '--out-file', default='./webserver-configuration', required=False, help='Filename where the generated Output should stored.')
        parser.add_argument('-op', '--out-file-node-provisioning', default='./node_provisioning.json', required=False, help='Filename where the generated Output should stored.')
        parser.add_argument('-v', '--debug', required=False, action='store_true', help='Enable debugging output.')
        parser.add_argument('-f', '--filters', nargs='*', required=False, choices=('exclude_clouds_with_lan_links', 'no_lan', 'domain_transitions_only'), help='Filter out nodes and local clouds based on filter rules.')
        parser.add_argument('-i', '--info', nargs='*', required=False, choices=('get_offline_nodes','offline'), help='Get infos about the graph, links and nodes.')
        parser.add_argument('-if', '--info-filters', nargs='*', required=False, help='Filter info results. Currently supported: min_age:TIME_RANGE, max_age:TIME_RANGE. Examples: -if min_age:1d max_age:2w')
        parser.add_argument('-iop', '--info-out-path', required=False, default='./', help='Folder where info files should be written. Default: ./')
        parser.add_argument('-iot', '--info-out-type', nargs='+', required=False, default='csv', choices=('json', 'csv'), help='Defines the format of info output. Default: csv')
        parser.add_argument('-ot', '--offline-threshold', nargs='?', required=False, type=int, const=int, default=20, help='The threshold when a node is classified as offline. In minutes.')

        return parser.parse_args()
NodeHierarchy()
