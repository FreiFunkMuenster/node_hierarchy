from info.InfoMeta import InfoMeta
from shapely.geometry import Point
import datetime, re
from datetime import timedelta
class OfflineInfo(InfoMeta):
    def __init__(self, filters, nodes, domains):
        super().__init__()
        self.__filters__ = filters
        self.__nodes__ = nodes
        self.__domains__ = domains
        self.__minAge__, self.__maxAge__ =  self.__parseFilters__()
        self.resultNodes = self.__filterNodes__()
    
    def __filterNodes__(self):
        
        offlineNodes = []
        
        for k,v in self.__nodes__.items():
            if v.isOnline == False:
                if v.geo != None:
                    for dk, dv in self.__domains__.items():
                        if dv.isPointInDomaene(Point((v.geo['lon'], v.geo['lat']))) == True:
                            nodeLastSeen = datetime.datetime.strptime(v.__jsonObject__['lastseen'],'%Y-%m-%dT%H:%M:%S.%fZ')
                            if self.__minAge__ != None:
                                if self.__minAge__ < nodeLastSeen:
                                    continue
                            if self.__maxAge__ != None:
                                if self.__maxAge__ > nodeLastSeen:
                                    continue
                            offlineNodes.append(v)
        
        return offlineNodes
        
    
    def __parseFilters__(self):
        
        if self.__filters__ == None:
            return None, None
        
        regX = re.compile("([0-9]+)([a-zA-Z]+)")
        minAge = None
        maxAge = None
        
        for filter in self.__filters__:
            attr = filter.split(':')
            if len(attr) == 2:
                if attr[0] == 'min_age' or attr[0] == 'max_age':
                    d = regX.match(attr[1])
                    if d != None:
                        val = int(d.group(1))
                        unit = d.group(2)
                        date = datetime.datetime.now()
                        if unit == 'd' or unit == 'day' or unit == 'days':
                            date = date - timedelta(days=val)
                        elif unit == 'w' or unit == 'week' or unit == 'weeks':
                           date = date - timedelta(days=val*7) 
                        elif unit == 'm' or unit == 'month' or unit == 'months':
                           date = date - timedelta(days=val*30) 
                        elif unit == 'y' or unit == 'year' or unit == 'years':
                           date = date - timedelta(days=val*365)
                        else:
                            date = None
                        
                        if attr[0] == 'min_age':
                            minAge = date
                        elif attr[0] == 'max_age':
                            maxAge = date
        return minAge, maxAge 
