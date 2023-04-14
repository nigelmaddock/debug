#!/usr/bin/python3 

from twisted.web import server, resource
from twisted.internet import reactor, endpoints
import cgi
import sys
import re

from xml.dom.minidom import parse, parseString

import requests

class Counter(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        return content.encode("ascii")

    def render_POST(self, request):
        doc = parseString(request.content.read())
        #print (doc.toprettyxml())
        #print ("###")

        timeNode = doc.getElementsByTagName("time")[0]
        textNode = timeNode.firstChild
        print ("time = " + textNode.data)
    
        eventNode = doc.getElementsByTagName("event")[0]
        textNode = eventNode.firstChild
        print ("message = " + textNode.data)


        searchString = ".*cf.fsm.partnerNotResponding.*"

        found = re.search(searchString, textNode.data)
        if (found):
            print ("Found cf.fsm.partnerNotResponding")


            req = '{"node": "azurecvoha-01", "dump": true}'
            url = 'https://172.16.1.12/api/private/cli/system/node/reboot?privilege_level=advanced'


            x = requests.post(url, data = req, auth = ('admin','Netapp1!'), verify=False)

            print (x)


        else:
            print ("not the one we're looking for")


        #while True:
        #    byte = request.content.read(1) # <--- read one byte
        #    if len(byte) > 0:
        #        sys.stdout.write(repr(byte))
        #        sys.stdout.flush()
        #    else:
        #        break
        #sys.stdout.write('\nfinished ' + str(request) + '\n')
        #sys.stdout.flush()

        content = u"Fish\n"
        return content.encode("ascii")


endpoints.serverFromString(reactor, "tcp:80").listen(server.Site(Counter()))
reactor.run()
