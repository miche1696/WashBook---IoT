import json
import time
import requests
import paho.mqtt.client as PahoMQTT
from datetime import datetime
from RushHour_Handler_V6 import*

class Power_Control(object):
	def __init__(self,topic, broker, Client_id, portnb, QoS, cat_url, TS_url, pi_url,catalog_port):
	
		self.broker = broker
		self.topic = topic
		self.Client_id=Client_id
		self.portnb=portnb
		self.QoS=QoS
		self.cat_url=cat_url
		self.TS_url=TS_url
		self.pi_url=pi_url
		self.catalog_port=catalog_port

		self.nMon=0
		self.m_used=[]
		self.m_booked=[]
		self.m_on=[]
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.Client_id, False)
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived

 
	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.broker, rc))


	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.broker, self.portnb)
		self._paho_mqtt.loop_start()
		self._paho_mqtt.subscribe(self.topic, self.QoS)

	def stop (self):
		self._paho_mqtt.unsubscribe(self.topic)
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		# A new message is received
		self.m_used=[]
		message=json.loads(msg.payload)
		for i in message.values():
			self.m_used.append(i)


	def time_generator(self):
		day=datetime.today()
		day=day.isoweekday()
		now = datetime.now()
		hour=now.hour
		return [day,hour]

	def handle_data(self):
		l1=self.time_generator()
		self.m_booked=[]
		url=self.TS_url+f'1&hour={l1[1]}&day={l1[0]}'
		bookings=requests.get(url)
		a=bookings.content
		self.m_booked=json.loads(a)
		return self.m_booked

	def nMon_generator(self):
		self.m_on=[]
		url=self.TS_url+'1'
		self.nMon=0
		for i in range(len(self.m_booked)):
			self.m_on.append(True)
		
		for i in range(len(self.m_on)):
			if self.m_on[i] and self.m_used[i]:
				self.nMon+=1

		l1=self.time_generator()
		Msg={"value":[self.nMon,l1[1],l1[0]]}
		Msg=json.dumps(Msg)
		requests.post(url,data=Msg)
		return self.nMon

	def catalog(self):
		"""docstring for alive"""
		url=self.pi_url+self.catalog_port+"/user"
		thing={"username":"power_control"} #hetet 4 randomly
		thing=json.dumps(thing)
		alive=requests.post(url,data=thing)

if __name__=="__main__":
	Broker=''
	Topic=''
	Clientid=''
	Portnb=''
	QoS=''
	URL_base=''
	URL_thingSpeak=''
	URL_pi=''
	catalog_port=''

	try:
		file=open("config.json")
		content=json.loads(file.read())
		Broker=content["Broker_MQTT"]
		Topic=content["topic"]
		Clientid=content["Client_id"]
		Portnb=content["Port_MQTT"]
		RushHour_port=content["RushHour_Handler_port"]
		QoS=content["QoS"]
		URL_base=content["URL_Base"]
		URL_thingSpeak=content["URL_thingSpeak"]
		URL_pi=str(content["URL_Pi"])
		catalog_port=str(content["catalogue_port"])
		file.close()
	except:
		print("Errors occured while opening configuration file")	

	print(Broker,Topic,Clientid,Portnb,RushHour_port,QoS,URL_base,URL_thingSpeak,URL_pi,catalog_port)
	a1=Power_Control(Topic,Broker,Clientid,Portnb,QoS,URL_base,URL_thingSpeak,URL_pi,catalog_port)
	
	try:
		a1.start()
	except:
		print("Couldn't connect to broker, please check the if topic and broker name are correct")
	try:	
		a1.catalog()
	except:
		print("Couldn't register power control service in catalog")
	
	hours=[]

	while(True):
		l1=a1.time_generator()

		if l1[1] not in hours:
			try:
				a1.handle_data()
				result=a1.nMon_generator()
				print(result)	
			except:
				print("Couldn't connect to database..")
			hours.append(l1[1])
		if l1[1]==23:
			hours=[]
		if l1[0]==6 and l1[1]==3:
			try:
				url=URL_base+f'{RushHour_port}/1'
				print(url)
				a=requests.get(url)
				a=a.content
				a=json.loads(a)
				print(a)
			except:
				print("Something went wrong with the price generation..")
		
		
	a1.stop()
		