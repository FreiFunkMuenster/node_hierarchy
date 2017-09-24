from parser.JsonParser import JsonParser
from shapely.geometry import shape
class ShapesParser(JsonParser):
    def __init__(self, filePath, targetName):
        super().__init__(filePath.rstrip('/') + '/' + targetName + '.geojson')
        self.shapes = self.__createShapes__()
  
    def __createShapes__(self):
        shapes = []
        if 'features' in self.__jsonData__:
            for feature in self.__jsonData__['features']:
                shapes.append(shape(feature['geometry']))
        elif 'geometries' in self.__jsonData__:
            for geometry in self.__jsonData__['geometries']:
                shapes.append(shape(geometry))

        return shapes
