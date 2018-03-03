#sample_4
from __future__ import print_function

from itty import *
import urllib2

#sample_4

import sys
from argparse import ArgumentParser
from util import get_url
import json
import logging
import requests

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    
def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents
    
           
def get_host(ip=None, mac=None):
    if ip is not None:
        url = "host?hostIp=%s" % ip
    elif mac is not None:
        url = "host?hostMac=%s" % mac
    return get_url(url)

def print_host(retrieved_host):
    #print(json.dumps(host, indent=2))

        connection = "-> {dev}|{interface}|vlan:{vlan}".\
            format(dev=retrieved_host['connectedNetworkDeviceIpAddress'],
                   interface=retrieved_host['connectedInterfaceName'],
                   vlan=retrieved_host['vlanId'])
        ip = retrieved_host['hostIp']+'|'
        mac = retrieved_host['hostMac']+'|'
        type = retrieved_host['hostType']
        connection = connection
        spark_word = ip+mac+type+connection
        spark_word_string = str(spark_word)
        print(spark_word_string)
        return spark_word_string

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message,
    """
    
    webhook = json.loads(request.body)
    #print (webhook)
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        if 'jarvis' in in_message:
            msg = "Who is there? Is that Tony?"
        elif 'no' in in_message:
            msg = "Salute to my new master!"
        elif 'who are you' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": jarvis_signal})
            msg = "J.A.R.V.I.S. - Just A Rather Very Intelligent Sparkbot"
        elif 'show' in in_message:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": friday_signal})
            msg = "T.G.I.Friday, the class is dismissed!"
        elif 'host' in in_message:
            in_message = result.get('text').split('host')[1].strip(" ")
            retrieved_host = get_host(str(in_message), mac=None)
            a = print_host(retrieved_host['response'][0])
            spark_title = "-----IP------------MAC----------CONNECTION--------INTERFACE--------VLAN-"
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": spark_title})
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": a})
        elif '10.' in in_message:
            retrieved_host = get_host(str(in_message), mac=None)
            a = print_host(retrieved_host['response'][0])
            spark_title = "-----IP------------MAC----------CONNECTION--------INTERFACE--------VLAN-"
            print(spark_title)
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": spark_title})
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": a})
        else:
            word = requests.request("GET","http://sandbox.api.simsimi.com/request.p?key=0b33d569-517e-49bd-a680-06af11e8e835&lc=en&ft=1.0&text=%s" % in_message) 
            new_word = word.text
            new_word_2 = new_word[1:-1]
            new_list = new_word_2.split(",")
            new_response = new_list[0]
            new_response_2 = new_response.split(":")
            new_response_3 = new_response_2[1]
            new_response_4 = new_response_3[2:-1]
            print(new_response_3)
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": new_response_4})

        if msg != None:
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
        
    return "true"

        

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('--ip', type=str,
                        help="ip address")
    parser.add_argument('--mac', type=str,
                        help="mac address")
    parser.add_argument('-v', action='store_true',
                        help="verbose")
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    


####CHANGE THESE VALUES#####
bot_email = "mr.jarvis@sparkbot.io"
bot_name = "Mr. J.A.R.V.I.S."
bearer = "NzFhODM3NDgtMzEwZC00ODg5LTg4ZDUtMmE5MzI4ZmRlY2I4YWVmNDgxMjUtYWMy"
friday_signal = "https://vignette.wikia.nocookie.net/marvelmovies/images/8/82/FRIDAY.jpg"
jarvis_signal = "https://vignette.wikia.nocookie.net/marvelmovies/images/0/06/J.A.R.V.I.S..jpg"
run_itty(server='wsgiref',host='0.0.0.0',port=10010)