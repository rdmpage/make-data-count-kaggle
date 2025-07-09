import xmltodict
import pprint
import json
import os

filename = '10.1186_s13059-020-1949-z.xml'
xml_folder = 'explore'

filename = 'output.xml'
filename = 'w.html'
xml_folder = '.'


xml_path = os.path.join(xml_folder, filename)

with open(xml_path) as fd:
    doc = xmltodict.parse(fd.read())
    
print(json.dumps(doc))

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(json.dumps(doc))
