import json
import paho.mqtt.client as PahoMQTT
import requests
import cherrypy
import time
import datetime

class Missed_Booking:
	def __init__(self,broker,port):
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client("Missed_Booking", False) 

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived

		self.topic = 'Weight_Sensor'
		self.broker = broker
		self.port= port
		self.mymessage=0
	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.broker,self.port)
		self._paho_mqtt.loop_start()
		self._paho_mqtt.subscribe(self.topic,2)

	def stop (self):
		self._paho_mqtt.unsubscribe(self.topic)
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		# A new message is received
		message_mqtt=json.loads(msg.payload)
		self.mymessage=message_mqtt


def main():
	print("Starting Penality Service")
	room_penalty_dict={}
	room_penalty_miss={}
	WM_list=[]
	zeros_list=[]
	print("Getting Data from Config File")
	try:
		f=open("config.json", "r")
	except:
		print("Problem getting data from config file")
	contents =f.read()
	contents=json.loads(contents)
	Num_WM=contents["washing_machines"]
	pen_miss=contents["penalty_on_miss"]
	pen_mult=contents["penalty_on_multiple_usage"]
	URL_thingSpeak=contents["URL_thingSpeak"]
	broker=contents["Broker_MQTT"]
	port=contents["Port_MQTT"]
	mult_pen_limit=contents["booking_limit"]
	URL_Base=contents["URL_Base"]
	catalogue_port=str(contents["catalogue_port"])
	URL_Pi=str(contents["URL_Pi"])
	f.close()
	print("Data retrieved from config file successfuly")
	print("Registering in Catalog")
	thing={"username":"penalty"}
	thing=json.dumps(thing)
	try:
		alive=requests.post(URL_Pi+catalogue_port+"/user",data=thing)
		print("Registered in catalog successfuly")
	except:
		print("Problem registering to catalog")
	for i in range(Num_WM):
		var="WM"+str(i+1)
		WM_list.append(var)
	print("Connecting to broker")
	sub = Missed_Booking(broker,port)
	try:
		sub.start()
	except:
		print("problem connecting to borker")
	print("Connected to broker")
	a=1
	b=1
	last_transmission=0
	print("Activating Services")
	while(True):
		date = datetime.datetime.now()
		day=date.weekday()+1
		hour=date.hour
		#To make sure that the penalties that are time bound are executed once and only once
		if hour==22 and day==7:
			a=0
			b=0
		# Do everytime the sensor sends a message, checks if booking missed
		if sub.mymessage!=0:
			message=sub.mymessage
			print("Sensor Data Received")
			print(message)
			print("Message from sensors received, processing...")
			print("Fetching bookings from database")
			link=URL_thingSpeak+"1&hour="+str(hour)+"&day="+str(day)
			try:
				response=requests.get(link)
				BookedWM=json.loads(response.content)
				print("Bookings received")
			except:
				error_fetch="failed fetching booked rooms at time "+hour+" on day "+day
				print(error_fetch)
				exit()
			print("Setting missed bookings to respective rooms")
			if len(BookedWM)!=0:
				for i in range(len(BookedWM)):
					if message[WM_list[i]]==0:
						if BookedWM[i] in room_penalty_miss:
							room_penalty_miss[BookedWM[i]]+=pen_miss
						else:
							room_penalty_miss[BookedWM[i]]=pen_miss
			sub.mymessage=0
			##################### For demonstration purposes
			last_transmission=1
			a=0
			b=0
			#####################
			print("Finished processing missed bookings")
			if day==7 and hour==11:
				last_transmission=1



 		#	Do every Sunday Night at at 11 save and confirm all penalties:
 		#	Checks who booked above limit and sets penalty as well as combines it with penalty of missed bookings
 		# if day==7 and hour==23 and a==0 and last_transmission==1:
		if day==3 and hour==12 and a==0 and last_transmission==1: #for demonstration
			a=1
			last_transmission=0
			print("Registering a complete record of all penalties between overbooking and missed bookings (done once every Sunday at 23:00)")
			link=URL_thingSpeak+"0"
			try:
				print("Fetching Library to check for multiple bookings above limit")
				body=requests.get(link).json()
			except:
				print("Error fetching thingspeak database")
				exit()
			print("Processing library...")
			for i in range(len(body['feeds'])):
				if body['feeds'][i]['field4'] in room_penalty_dict:
					room_penalty_dict[body['feeds'][i]['field4']] += 1
				else:
					room_penalty_dict[body['feeds'][i]['field4']] = 1
			del room_penalty_dict[None]
			for i in room_penalty_dict:
				if room_penalty_dict[i]>mult_pen_limit:
					room_penalty_dict[i]=room_penalty_dict[i]*pen_mult
				else:
					room_penalty_dict[i]=0
			for i in room_penalty_miss:
					if i in room_penalty_dict:
						room_penalty_dict[i]+=room_penalty_miss[i]
					else:
						room_penalty_dict[i]=room_penalty_miss[i]
			room_penalty_miss.clear()
			print(room_penalty_dict)
			print("Removing zero penalties since they do not exceed threshold")
			for i in room_penalty_dict:
				if room_penalty_dict[i]==0:
					zeros_list.append(i)
			for i in zeros_list:
				del room_penalty_dict[i]
			print("All Penalties have been recorded. Ready to transmit!")
			print(room_penalty_dict)
			zeros_list.clear()



		# Do every monday morning at 0, update database with penalties
		# if day==1 and hour==0 and b==0: #for demonstration
		if day==3 and hour==12 and b==0:
			print("Updating database with penalties (done once every Monday at 00:00")
			b=1
			for i in room_penalty_dict:
				try:
					dict2=json.dumps({"value":[i,room_penalty_dict[i]]})
					x = requests.post(URL_thingSpeak+"2",data=dict2)
					string_success="Sent penalty for room: "+i
					print(string_success)
					time.sleep(0.1)
				except:
					string_error="Error occurred in setting the penalty for room: "+i
					print(string_error)
			room_penalty_dict.clear()
			print("Updating database with penalties complete")
	sub.stop()

if __name__ == '__main__':
	try:
		main()
	except:
		print("A problem has occured in main function...exiting")
		exit()