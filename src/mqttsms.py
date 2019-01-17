#! /usr/bin/python3

import logging
import gammu
import time
import getopt
import os
import paho.mqtt.client as mqtt
import json


def on_connect(mqttc, obj, flags, rc):
    logging.info("mqtt connected")

def on_diconnect(mqttc, obj, rc):
     logging.error("diconnect from mqtt")
     exit(1)

def on_message(mqttc, obj, msg):
    logging.info("receive message " +msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode("utf-8")))
    try:
        data=json.loads(msg.payload.decode("utf-8"))
        mqttc.publish(mqttTopic+'send/feedback',json.dumps({'code': 'OK','message':data},ensure_ascii = False))
        sendSMS(data['phone'],data['text'])
    except:
        mqttc.publish(mqttTopic+'send/feedback',json.dumps({'code': 'ERROR','message':msg.payload.decode("utf-8")},ensure_ascii = False))

def sendSMS(phone, text):
    smsinfo = {
        'Class': -1,
        'Unicode': True,
        'Entries':  [
            {
                'ID': 'ConcatenatedTextLong',
                'Buffer': text
            }
        ]}
    encoded = gammu.EncodeSMS(smsinfo)

    for message in encoded:
        # Fill in numbers
        message['SMSC'] = {'Location': 1}
        message['Number'] = phone

        # Actually send the message
        sm.SendSMS(message)


# main

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# mqtt connect
mqttc = mqtt.Client()
mqttHost = os.getenv('MQTT_HOST', 'localhost')
mqttPort = int(os.getenv('MQTT_PORT', '1883'))
mqttUser = os.getenv('MQTT_USER', '')
mqttPwd = os.getenv('MQTT_PWD', '')
mqttTopic = os.getenv('MQTT_TOPIC', '/sms/')

if  mqttUser :
    mqttc.username_pw_set(mqttUser, mqttPwd)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_diconnect = on_diconnect

rc = mqttc.connect(mqttHost, mqttPort, 60)
if rc != 0:
    logging.error("Connection failed with error code %s. Retrying", result)
    exit(1)

mqttc.subscribe(mqttTopic+'send')
mqttc.loop_start()


# connect to gammu
sm = gammu.StateMachine()
sm.ReadConfig()
sm.Init()


while 1:
    status = sm.GetSMSStatus()
    remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    sms = []
    start = True
    while remain > 0:
        if start:
            cursms = sm.GetNextSMS(Start = True, Folder = 0)
            start = False
        else:
            cursms = sm.GetNextSMS(Location = cursms[0]['Location'], Folder = 0)
        remain = remain - len(cursms)
        sms.append(cursms)
        sm.DeleteSMS(Location = cursms[0]['Location'],Folder=0);

    data = gammu.LinkSMS(sms)

    for x in data:
        v = gammu.DecodeSMS(x)
        m = x[0]
        msg={}
        msg['Phone']= m['Number']
        msg['Date']= str(m['DateTime'])
        msg['State']= m['State']
        msg['Text']= m['Text'] if v == None else v['Entries'][0]['Buffer']
        
        logging.info(msg)
        mqttc.publish(mqttTopic+'receive', json.dumps(msg, ensure_ascii = False))
        
    time.sleep(50)
exit(0)





        