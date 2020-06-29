import paho.mqtt.client as PahoMQTT
import time
import datetime
import random
import json
import threading
import requests

class Weight_Sensor(threading.Thread):
	def __init__(self, clientID, broker, port, Num_WM,Qos):
		threading.Thread.__init__(self)
		self.clientID = clientID
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
		self._paho_mqtt.on_connect = self.myOnConnect
		self.messageBroker = broker
		self.port=port
		self.Num_WM=Num_WM
		self.Qos=Qos
		self.test=1
	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

	def run(self):
		########### Just to have enough time to observe on CMD
		time.sleep(5)
		###########
		WM_dict={}
		for i in range(self.Num_WM):
			name="WM"+str(i)
			WM_dict[name]=0
		print("Connecting to broker")
		self._paho_mqtt.connect(self.messageBroker, self.port)
		self._paho_mqtt.loop_start()
		print("Connected to broker")
		while(True):
			time.sleep(5)
			time1 = datetime.datetime.now()
			while(True):
				time2=datetime.datetime.now()
				difference=time2-time1
				duration_in_s = difference.total_seconds()
				duration_in_hours = duration_in_s/3600
				######################### TO TEST CODE INSTEAD OF WAITING THE FIRST HOUR
				if self.test==1:
					duration_in_hours+=1
					self.test=0
				#########################
				if duration_in_hours>=1:
					print("Time to publish sensor data (done every hour)")
					for i in WM_dict:
						WM_dict[i]=random.random()
						if WM_dict[i]>0.1:
							WM_dict[i]=1
						else:
							WM_dict[i]=0
					time1=datetime.datetime.now()
					msg = json.dumps(WM_dict)
					self._paho_mqtt.publish('Weight_Sensor', msg, self.Qos)
					print("Sensor Data Sent: ")
					print(WM_dict)
				time.sleep(1)
		print("Disconnected From Broker")
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

class alive(threading.Thread):
	"""docstring for alive"""
	def __init__(self,URL_catalogue):
		threading.Thread.__init__(self)
		self.URL_catalogue=URL_catalogue
		
	def run(self):
		print("Regiserting to Catalog")
		thing={"Username":"Weight_Sensor"}
		thing=json.dumps(thing)
		try:
			print("Attempting Connection to catalog")
			alive=requests.post(URL_catalogue+"/device",data=thing)
			print("Post Sent to Catalog")	
		except:
			print("A problem has occured while registering to catalog...exiting")
			exit()
		while True:
			time.sleep(60)
			try:
				alive=requests.put(URL_catalogue+"/device?ID=1")
				print("Catalog Updated")
			except:
				print("A problem has occured maintaing connection to catalog...exiting")
				exit()




if __name__ == '__main__':
	print("Initializing")
	print("Getting Data from Config File")
	f=open("config.json", "r")
	contents =f.read()
	contents=json.loads(contents)
	Num_WM=contents["washing_machines"]
	broker=contents["Broker_MQTT"]
	port=contents["Port_MQTT"]
	URL_Base=str(contents["URL_Base"])
	catalogue_port=str(contents["catalogue_port"])
	URL_Pi=str(contents["URL_Pi"])
	Qos=contents["QoS"]
	URL_catalogue=URL_Pi+catalogue_port
	f.close()
	print("Data retrieved from Config File")




	thread1=Weight_Sensor('Washing Machine Sensor',broker,port,Num_WM,Qos)
	thread2=alive(URL_catalogue)

	try:
		thread2.start()
	except:
		print("A problem has occured in catalog thread...exiting")
		exit()
		
	try:
		thread1.start()
		print("Starting Sensors")
	except:
		print("A problem has occured in sensor thread...exiting")
		exit()