# Node Hierarchy
Dieses Tool generiert auf Basis einer ``raw.json`` des [hopglass-server](https://github.com/hopglass/hopglass-server) sowie (Multi-)Polygonen (im [geojson](http://geojson.org/) Format) der einzelnen Zieldomänen eine [nginx](http://nginx.org/) Konfigurationsdatei (auf Basis des [Geo-Moduls](http://nginx.org/en/docs/http/ngx_http_geo_module.html)), um Knoten in der richtigen Reihenfolge umzuziehen.


## Vorgehensweise
Das Tool zerteilt den (globalen) Graphen in viele lokale Graphen, also die Menge an Knoten (und Links), die vor Ort ein Mesh bilden. Diese werden auf Basis der Shapefiles den einzelnen Zieldomänen zugeordnet (es werden die Geopositionen der einzelnen Knoten "gemittelt"). Hier wird nun geprüft, welche Knoten keine Abhängigkeiten besitzen, also kein anderer Knoten über diesen Knoten gehen muss, um einen Gatewayserver zu erreichen. Diese werden dann in die Konfiguration geschrieben.

Sind diese Knoten aktualisiert, fällt die Abhängigkeit des Knoten weg, der zuvor benötigt wurde, um das Gateway zu erreichen. Daher muss das Tool regelmäßig ausgeführt und die Ausgabe jeweils in die nginx-Konfiguration übernommen werden.


## Abhängigkeiten
Das Tool läuft ausschließlich mit **Python >= 3**.
Folgende (Python-)Abhängigkeiten werden benötigt:

- [shapely](https://pypi.python.org/pypi/Shapely)

Diese lassen sich wie folgt via [pip](https://pypi.python.org/pypi/pip) installieren:

```
pip3 install shapely
```


## Bedienung
Das Tool wird ausschließlich über Argumente beim Aufruf konfiguriert.

Die Hilfe liefert folgendes:

```
usage: NodeHierarchy.py [-h] [-r RAW_JSON] [-s SHAPES_PATH] -t TARGETS [TARGETS ...] [-sttp SITE_TO_TARGET_PREFIX] [-o OUT_FILE] [-op OUT_FILE_NODE_PROVISIONING] [-v]
                        [-f [{exclude_clouds_with_lan_links,no_lan,domain_transitions_only} ...]] [-i [{get_offline_nodes,offline} ...]] [-if [INFO_FILTERS ...]] [-iop INFO_OUT_PATH]
                        [-iot {json,csv} [{json,csv} ...]] [-ot [OFFLINE_THRESHOLD]]

This Script generates a hierarchical nodes list for node migration using nginx geo feature.

options:
  -h, --help            show this help message and exit
  -r RAW_JSON, --raw-json RAW_JSON
                        Location of raw.json file (can be local folder or remote URL).
  -s SHAPES_PATH, --shapes-path SHAPES_PATH
                        Path of shapefiles (can be local folder or remote URL).
  -t TARGETS [TARGETS ...], --targets TARGETS [TARGETS ...]
                        List of targets which should be proceeded. Example: -t citya cityb ...
  -sttp SITE_TO_TARGET_PREFIX, --site-to-target-prefix SITE_TO_TARGET_PREFIX
                        Used to match site and target also when prefixes are different. Example: -sttp "ffmsd,domaene"
  -o OUT_FILE, --out-file OUT_FILE
                        Filename where the generated Output should stored.
  -op OUT_FILE_NODE_PROVISIONING, --out-file-node-provisioning OUT_FILE_NODE_PROVISIONING
                        Filename where the generated Output should stored.
  -v, --debug           Enable debugging output.
  -f [{exclude_clouds_with_lan_links,no_lan,domain_transitions_only} ...], --filters [{exclude_clouds_with_lan_links,no_lan,domain_transitions_only} ...]
                        Filter out nodes and local clouds based on filter rules.
  -i [{get_offline_nodes,offline} ...], --info [{get_offline_nodes,offline} ...]
                        Get infos about the graph, links and nodes.
  -if [INFO_FILTERS ...], --info-filters [INFO_FILTERS ...]
                        Filter info results. Currently supported: min_age:TIME_RANGE, max_age:TIME_RANGE. Examples: -if min_age:1d max_age:2w
  -iop INFO_OUT_PATH, --info-out-path INFO_OUT_PATH
                        Folder where info files should be written. Default: ./
  -iot {json,csv} [{json,csv} ...], --info-out-type {json,csv} [{json,csv} ...]
                        Defines the format of info output. Default: csv
  -ot [OFFLINE_THRESHOLD], --offline-threshold [OFFLINE_THRESHOLD]
                        The threshold when a node is classified as offline. In minutes.

```


### Anmerkungen

- ``--targets`` Gibt die Namen der Ziele (Zieldomänen) an. Der Geo-Schalter in der nginx-Konfiguration wird ebenfalls diesen Namen tragen.
- ``--raw-json`` Gibt den Ort der raw.json (hopglass-server) an. Default: ``https://karte.freifunk-muensterland.de/data/raw.json``
- ``--shapes-path`` Verzeichnis an dem die Shapefiles der einzelnen Ziel-Domänen liegen. Default: ``https://freifunk-muensterland.de/md-fw-dl/shapes/``
  - *Anmerkung:* Es werden Dateien in Abhängigkeit mit den Target-Namen im Verzeichnis erwartet.
  - *Beispiel:* Bei ``-targets domaene01 domaene02`` werden die Dateien ``domaene01.geojson`` und ``domaene02.geojson`` erwartet.
  - Falls ihr hier mehr Anpassbarkeit benötigt, eröffnet ein Issue, dann baue ich da was ein.
- ``--filters`` Siehe Abschnitt *Filter*.

Der Rest ist trivial.


### Filter
Standardmäßig werden alle Knoten ausgefiltert, die offline sind. Außerdem werden alle lokalen Wolken ausgefiltert, in denen sich mindstens ein Knoten mit deaktiviertem Autoupdater befindet.

Weitere Filterungen lassen sich über das ``--filters`` Attribut aktivieren.

Folgende Filter sind derzeit implementiert (zukünftig folgen noch weitere):

- ``exclude_clouds_with_lan_links`` bzw. ``no_lan`` filtert alle lokalen Wolken aus, in denen sich mindestens ein Mesh-on-LAN Link befindet
- ``domain_transitions_only`` filtert alle Knoten aus, die sich bereits in der richtigen Domäne befinden / die Firmware der richtigen Domäne besitzen


## Nginx Konfiguration
Das Tool generiert nur Konfigurationscode, der Schalter auf Basis von IPv6-Adressen beinhaltet. Die Auswirkungen, die diese Schalter haben sollen, müsst ihr noch selbst definieren. Typischerweise möchte man auf Basis der Schalter einen Rewrite machen.

Beispiel:

```
if ($domaene01) {
  rewrite ^/site-ffms/(.*)$ /domaene01/$1; 
}
```

*Anmerkung:* Bei $domane01 handelt es sich um den generierten Schalter, entspricht also ``--targets domaene01``.


## Info-Modul
Über das Info-Modul ist es möglich Informationen über Knoten, Links, Graphen und Domänen zu erstellen. Diese Informationen können entweder in ``csv``-Dateien oder in ``json``-Dateien gespeichert werden. Derzeit ist nur das Modul ``get_offline_nodes`` verfügbar. Zusätzlich lassen sich an das Info-Modul Filter übergeben.

### Offline-Knoten
Gibt Informationen zu Knoten aus, die offline sind. Dazu gibt es die folgenden beiden Filter:

 - ``min_age:TIME_RANGE``: Knoten, die eine kürzere Zeit als die angegebene Zeit offline sind, werden ignoriert.
 - ``max_age:TIME_RANGE``: Knoten, die eine längere Zeit als die angegebene Zeit offline sind, werden ignoriert.
 
 Dabei setzt sich ``TIME_RANGE`` aus zwei Teilen zusammen:
 - (Integer) Wert
 - Einheit:
   - ``d``, ``day`` oder ``days``: Der Wert wird als eine Anzahl von Tagen interpretiert.
   - ``w``, ``week`` oder ``weeks``: Der Wert wird als eine Anzahl von Wochen interpretiert.
   - ``m``, ``month`` oder ``months``: Der Wert wird als eine Anzahl von Monaten (30 Tage) interpretiert.
   
Der Beispielaufruf 

``$ ./NodeHierarchy.py -t domaene01 -i get_offline_nodes -if max_age:2w min_age:1d``

schreibt in die Datei ``./offline_nodes.csv`` (default-Einstellung der Schalter ``-iop`` und ``-iot``) Informationen zu Knoten die länger als einen Tag aber kürzer als zwei Wochen offline sind (im CSV-Format).


## Bekannte Probleme
Wenn es sich bei der Quell-Domäne um eine L2TP-Domäne handelt, läuft das Tool derzeit nur, wenn [alfred](https://github.com/ffnord/ffnord-alfred-announce) oder respondd auf allen Gateway-Servern läuft.

*Anmerkung:* Wenn in der ``graph.json`` mehrere Domänen vorhanden sind und dort teilweise L2TP-Domänen vorhanden sind (dieses aber nicht das Gebiet eurer Zieldomäne betrifft), kann das sehr negative Auswirkungen auf die Laufzeit haben (> 30 Sekunden).


## Lizenz
Dieses Tool unterliegt der MIT Lizenz.
Solltet ihr Probleme mit dieser Lizensierung haben, schreibt mich einfach an. ;)

2016 - Simon Wüllhorst
