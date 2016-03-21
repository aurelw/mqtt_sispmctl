#!/usr/bin/python3

###
# Copyright 2015, Aurel Wildfellner.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import time
import argparse
import os

import mosquitto
import topicconfig
from topictypes import TopicTypes



def on_message(client, userdata, msg):
    """ Callback for mqtt message."""
    payload = msg.payload.decode("utf-8")
    for ctopic in topicconfig.outlet_topics:
        
        if ctopic['topic'] == msg.topic:
            
            if ctopic['type'] == TopicTypes.TOGGLE_ON_TOPIC:
                os.system("sispmctl -t " + str(ctopic['outlet']))
            elif ctopic['type'] == TopicTypes.POWERON_ON_TOPIC:
                os.system("sispmctl -o " + str(ctopic['outlet']))
            elif ctopic['type'] == TopicTypes.POWEROFF_ON_TOPIC:
                os.system("sispmctl -f " + str(ctopic['outlet']))

            if "payload" in ctopic.keys() and payload == ctopic['payload']:
                if ctopic['type'] == TopicTypes.TOGGLE_ON_PAYLOAD:
                    os.system("sispmctl -t " + str(ctopic['outlet']))
                elif ctopic['type'] == TopicTypes.POWERON_ON_PAYLOAD:
                    os.system("sispmctl -o " + str(ctopic['outlet']))
                elif ctopic['type'] == TopicTypes.POWEROFF_ON_PAYLOAD:
                    os.system("sispmctl -f " + str(ctopic['outlet']))


def on_disconnect(client, userdata, foo):
    connected = False
    while not connected:
        try:
            client.reconnect()
            connected = True
            # resubscribe to the topics
            for ctopic in topicconfig.cat_topics:
                client.subscribe(ctopic['topic'])
        except:
            print("Failed to reconnect...")
            time.sleep(1)


def main():

    ## Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="test.mosquitto.org")

    args = parser.parse_args() 
    brokerHost = args.host
    
    ## setup MQTT client
    client = mosquitto.Mosquitto()
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(brokerHost)
    except:
        print("failed to connect")
        on_disconnect(client, None, None)

    ## subscribe to topics
    for ctopic in topicconfig.outlet_topics:
        client.subscribe(ctopic['topic'])

    while True:
        
        client.loop()


if __name__ == "__main__":
    main()

