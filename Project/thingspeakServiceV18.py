import urllib
import json
import time
import cherrypy
import http
import requests


class thingspeakService(object):
	exposed = True

	def __init__(self,WM,Key,Channel,Key2,Channel2,Key3,Channel3,Api_key,URL_Catalogue):
		self.availableWm=WM
		self.key=Key
		self.channel=Channel
		self.key2=Key2
		self.channel2=Channel2
		self.key3=Key3
		self.channel3=Channel3	
		self.api_key=Api_key
		self.URL_Catalogue=URL_Catalogue


	def GET(self, *uri,**params):
		# GET HAS TO BE CALLED WITH 2 PARAMETERS -> HOUR AND DAY , IN THIS EXACT ORDER #

		# The script takes the database from the thingspeak site and returns the actual number of WM booked in that
		# hour/day slot


		# !!!!!!! IMPORTANT !!!!!!!
		# COMMAND FEATURES:
		#
		# 0 TO GET THE WHOLE DATABASE
		#
		#
		# 1 TO GET THE LIST OF ROOMS THAT ARE BOOKED IN THE SLOT YOU ASK FOR. ORDERED IN BASE OF THE WM THAT IS USED (first in the list is uusing the first WM and so on)
		# PARAMS FORMAT =>   command=1   hours=X   day=Y
		# Example  				http://localhost:8080/thingspeakservice?command=1&hour=1&day=2
		# Example output  		["123", "234"]		->		[WM1RoomNumber, WM2RoomNumber]
		#
		#
		# 2 TO GET THE ACTUAL PENALTY AND THE TOTAL NUMBER OF MISSING SLOT OF A CERTAIN ROOM IN THIS EXACT ORDER
		# PARAMS FORMAT =>   command=2   room=X
		# Example  http://localhost:8080/thingspeakservice?command=2&room=2
		# Example output		["3", "0", "0"]    	->  	[RoomNumber, Charge, NumberOfMissedBookings]

		# 3 TO GET THE ACTUAL PRICE OF A CERTAIN SLOT
		# PARAMS FORMAT =>   command=3   hours=X   day=Y
		# Example  http://localhost:8080/thingspeakservice?command=3&hour=1&day=2
		# Example output		["2"]    	->  	[Price]


		# 4 TO GET THE FREE HOUR SLOTS IN A DAY
		# PARAMS FORMAT =>   command=4   Day=Y
		# Example  http://localhost:8080/thingspeakservice?command=4&day=2
		# Example output		["2,5,8,14"]    	
		var=0
		count=0
		lista=[]
		penalty=0
		missing=0
		penalty2=0
		missing2=0
		price=0
		command=int(params["command"])
		print("command =",command)

		if command==0 :
			TS = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel,self.key))
			response = TS.read()
			data=json.loads(response)
			print ("returning database")
			formatted=json.dumps(data,indent=3)
			TS.close()
			return formatted
		elif command==1 :
			TS = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel,self.key))
			response = TS.read()
			data=json.loads(response)
			hour=int(params["hour"])
			print("hour =",hour)
			day=int(params["day"])
			print("day =",day)
			print ("looking for rooms that booked in day/hour  = ", day , hour)
			for p in data['feeds']:
				if not p['field5']:	
					var=0 #useless, just to have a statement inside the if
				else:	
					if int(p['field5']) is hour:
						if int(p['field6']) is day:
							lista.append(p['field4'])
							count=count+1
							#print ("found one = ", p['field4'])
							#print ("total count =", count)
			TS.close()
			print ("returning count of day, hour, count", day, hour, count)
			return json.dumps(lista)
		elif command==2 :
			TS = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel,self.key))
			response = TS.read()
			data=json.loads(response)
			room=int(params["room"])
			print ("looking for penalty and missed bookings of room =", room)
			for p in data['feeds']:
				if not p['field4']:	
					var=0 #useless, just to have a statement inside the if
				else:	
					print("field4 presente")
					print("field4= ", p['field4'])
					if str(p['field4'])==str(room):
						if not p['field5']:
							if  p['field7']:
								print("field7= ", p['field7'])
								penalty2 =  p['field7']
							elif p['field8']:
								print("field8= ", p['field8'])
								missing2 = p['field8']
			TS.close()	
			print ("returning penalty and missed hours", room, penalty2, missing2)
			penalty=int(penalty2)
			missing=int(missing2)
		elif command==3 :
			TS = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel2,self.key2))
			response = TS.read()
			data=json.loads(response)
			hour=int(params["hour"])
			print("hour =",hour)
			day=int(params["day"])
			print("day =",day)
			print ("looking for price in day/hour  = ", day , hour)
			if day==0:
				campo='field1'
			elif day==1:
				campo='field2'
			elif day==2:
				campo='field3'
			elif day==3:
				campo='field4'
			elif day==4:
				campo='field5'
			elif day==5:
				campo='field6'
			elif day==6:
				campo='field7'
			for p in data['feeds']:	
				stringa=p[campo]
				stringa = stringa.split(',')
				return json.dumps(int(stringa[hour]))	
			return json.dumps("Your request is wrong, please verify the day you are providing")
		elif command==4 :
			TS = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel,self.key))
			response = TS.read()
			data=json.loads(response)
			day=int(params["day"])
			print ("looking for free hours in day = ", day)
			availableHours=[self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm,self.availableWm]
			for p in data['feeds']:
				if not p['field6']:	
					var=0 #useless, just to have a statement inside the if
				else:	
					if int(p['field6']) is day:
						toPop=int(p['field5'])
						availableHours[toPop]=availableHours[toPop]-1
			counter=0;
			vectorHours="";
			for x in availableHours:
				if x>0:
					vectorHours=vectorHours +str(counter) + ",";
				counter=counter+1;
			return json.dumps(vectorHours)	
		return json.dumps([room,penalty,missing])
			

		# If i want to print them #
		# formatted=json.dumps(data,indent=3)
		# print formatted

	def POST(self, **params):
		# ADDS DATA DO THE DATABASE

		# 	!!! IMPORTANT !!!
		# 	The PARAMS should be a number labeled "command":
		#
		# 	0 to add information about a booking
		# 	Example 				http://localhost:8080/thingspeakservice?command=0
		#	Example body			{"value" : [123,2,4]}			->		[Room,hour,day]
		#
		# 	1 to add information about the real usage of the WM in a certain hour
		# 	Example 				http://localhost:8080/thingspeakservice?command=1
		#	Example body			{"value" : [0,2,4]}			->		[WMon, hour, day]
		#
		# 	2 to add information about penalty
		# 	Example 				http://localhost:8080/thingspeakservice?command=2
		#	Example body			{"value" : [49,2]}			->		[Room,penalty]
		#
		# 	3 to add information about missing booked slot
		# 	Example 				http://localhost:8080/thingspeakservice?command=3
		#	Example body			{"value" : [49,4]}			->		[Room,missing]
		#
		# 	4 to add information about the price of a slot
		# 	Example 				http://localhost:8080/thingspeakservice?command=4
		#	Example body			{"value" : [1,2,3,...,167,168]} ->   all 24*7=168 prices, one for each correspondent slot
		#
		# 	5/6/7 to add information TO THE DASHBOARD
		# 	Example 				http://localhost:8080/thingspeakservice?command=5
		#	Example body			{"value" : [1,2,3,...,167,168]} ->   all 24*7=168 wh shop data usage, one for each correspondent slot


		datas = cherrypy.request.body.read()
		print(datas)
		_parseConstants = None
		dat=json.loads(datas, parse_constant=_parseConstants)
		datas=dat["value"]
		#datas = datas.split(',')
		command=str(params["command"])
		if command=="0":
			print ("Comand = 0")
			room=datas[0]
			hour=datas[1]		
			day=datas[2]
			
			params = urllib.parse.urlencode({'field4': room,'field5': hour,'field6': day, 'key':self.key }) 

			####################################
			####################################
			#
			# field4 = room number that is booking
			# field5 = hour
			# field6 = day
			#
			# These fields are used to decide in REAL TIME if we need to turn off/on WM
			# based on the actual usage of them
			#
			####################################
			####################################

			headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
			conn = http.client.HTTPConnection("api.thingspeak.com:80")
			try:
				conn.request("POST", "/update", params, headers)
				response = conn.getresponse()
				confirm= "Book correctly saved => Room {} booked a WM at hour {} of day {} . Status {} {}"
				print(confirm.format(room, hour, day,response.status, response.reason))
				print (response.status, response.reason)
				data = response.read()
				conn.close()
			except:
				print ("connection failed")	
				return "connection failed"
			print ("booking data saved correctly")
			return "Correctly saved"			
		elif command=="1":
			print ("Comand = 1")
			WMOn=datas[0]
			hour=datas[1]
			day=datas[2] 
			params = urllib.parse.urlencode({'field1': WMOn,'field2': hour,'field3': day, 'key':self.key })
			
			####################################
			####################################
			#
			#   Explanation
			#   field1 = number of WM used in that hour/day
			#   field2 = hour
			#   field3 = day
			#
			####################################
			#################################### 

			headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
			conn = http.client.HTTPConnection("api.thingspeak.com:80")
			try:
				conn.request("POST", "/update", params, headers)
				response = conn.getresponse()
				confirm= "WMOn correctly saved => {} WM are used at hour {} of day {} . Status {} {}"
				print(confirm.format(WMOn, hour, day,response.status, response.reason))
				data = response.read()
				conn.close()
			except:
				print ("connection failed")	
				return "connection failed"
			print ("WMOn data saved correctly")	
		elif command=="2" :
			print ("Comand = 2")
			room=datas[0]
			penalty=datas[1]

			params = urllib.parse.urlencode({'field4': room,'field7': penalty, 'key':self.key }) 

			####################################
			####################################
			#
			# field4 = room number that is booking
			# field7 = penalty
			#
			####################################
			####################################

			headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
			conn = http.client.HTTPConnection("api.thingspeak.com:80")
			try:
				conn.request("POST", "/update", params, headers)
				response = conn.getresponse()
				confirm= "Correctly saved => Room {} has a penalty of {} . Status {} {}"
				print(confirm.format(room, penalty ,response.status, response.reason))
				print (response.status, response.reason)
				data = response.read()
				conn.close()
			except:
				print ("connection failed")	
				return "connection failed"
			print ("penalty data saved correctly")
			return "Correctly saved"			
		elif command=="3":
			print ("Comand = 3")
			room=datas[0]
			missing=datas[1]

			params = urllib.parse.urlencode({'field4': room,'field8': missing, 'key':self.key }) 

			####################################
			####################################
			#
			# field4 = room number that is booking
			# field8 = miss
			#
			####################################
			####################################

			headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
			conn = http.client.HTTPConnection("api.thingspeak.com:80")
			try:
				conn.request("POST", "/update", params, headers) 
				response = conn.getresponse()
				confirm= "Correctly saved => Room {} missed {} bookings. Status {} {}"
				print(confirm.format(room, missing ,response.status, response.reason))
				print (response.status, response.reason)
				data = response.read()
				conn.close()
			except:
				print ("connection failed")	
				return "connection failed"
			print ("missed bookings data saved correctly")
			return "Correctly saved"
		elif command=="4":
			days = ["" for x in range(7)]
			days[0]=""
			days[1]=""
			days[2]=""
			days[3]=""
			days[4]=""
			days[5]=""
			days[6]=""
			print ("Comand = 4")	
			for x in range(0, 7):
				stringOfPrices=""


				for y in range(0, 24):
					if stringOfPrices != "" :
						stringOfPrices += ','
					stringOfPrices += str(datas[x*24+y])
				days[x]=stringOfPrices
			params = urllib.parse.urlencode({'field1': days[0],'field2': days[1],'field3': days[2], 'field4': days[3],'field5': days[4],'field6': days[5], 'field7': days[6],'key':self.key2 }) 

			####################################
			####################################
			#
			# field1 = day1
			# field2 = day2
			# field3 = day3 ...and so on
			#
			####################################
			####################################

			headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
			conn = http.client.HTTPConnection("api.thingspeak.com:80")
			try:
				conn.request("POST", "/update", params, headers)
				response = conn.getresponse()
				confirm= "Price correctly saved => Price {} at hour {} of day {} . Status {} {}"
				print (response.status, response.reason)
				data = response.read()
				conn.close()
			except:
				print ("connection failed")	
				return "connection failed"
			print ("price data saved correctly")
			return "Correctly saved"
		elif command=="5":
			print ("Comand = 5")
			try:
				for x in range(0, 8):	
					params = urllib.parse.urlencode({'field1': datas[x],'field2': datas[24+x],'field3': datas[24*2+x], 'field4': datas[24*3+x],'field5': datas[24*4+x],'field6': datas[24*5+x], 'field7': datas[24*6+x],'key':self.key3 }) 
					headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
					conn = http.client.HTTPConnection("api.thingspeak.com:80")					
					conn.request("POST", "/update", params, headers)
					response = conn.getresponse()
					print (response.status, response.reason, x)
					data = response.read()
					conn.close()
					time.sleep(15)
			except:
				print ("connection failed")	
				return "connection failed"
			print ("price data saved correctly")
			return "Correctly saved"
		elif command=="6":
			print ("Comand = 6")
			try:
				for x in range(8, 16):	
					params = urllib.parse.urlencode({'field1': datas[x],'field2': datas[24+x],'field3': datas[24*2+x], 'field4': datas[24*3+x],'field5': datas[24*4+x],'field6': datas[24*5+x], 'field7': datas[24*6+x],'key':self.key3 }) 
					headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
					conn = http.client.HTTPConnection("api.thingspeak.com:80")					
					conn.request("POST", "/update", params, headers)
					response = conn.getresponse()
					print (response.status, response.reason, x)
					data = response.read()
					conn.close()
					time.sleep(15)
			except:
				print ("connection failed")	
				return "connection failed"
			print ("price data saved correctly")
			return "Correctly saved"
		elif command=="7":
			print ("Comand = 7")
			try:
				for x in range(16, 24):	
					params = urllib.parse.urlencode({'field1': datas[x],'field2': datas[24+x],'field3': datas[24*2+x], 'field4': datas[24*3+x],'field5': datas[24*4+x],'field6': datas[24*5+x], 'field7': datas[24*6+x],'key':self.key3 }) 
					headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
					conn = http.client.HTTPConnection("api.thingspeak.com:80")					
					conn.request("POST", "/update", params, headers)
					response = conn.getresponse()
					print (response.status, response.reason, x)
					data = response.read()
					conn.close()
					time.sleep(15)
			except:
				print ("connection failed")	
				return "connection failed"
			print ("price data saved correctly")
			return "Correctly saved"	
		else:
			print ("Wrong command from url, use 0 (booking),  1 (WMOn), 2 (penalty), 3 (missing bookings), 4 (Slot price adding), 4 (dashboard data) ")
		return "Correctly saved"

	def PUT(self):
		return "PUT not used"

	def DELETE(self, **params):
		# DELETES THE WEEK DATABASES        COMMAND 0  ->  DELETE BOOKING DATABASE   COMMAND 1 -> DELETE PRICE DATABASE   COMMAND 2 -> DELETE DASHBOARD
		# EX    http://localhost:8080/thingspeakservice?command=0

		command=int(params["command"])
		print("command =",command)
		conn = http.client.HTTPConnection("api.thingspeak.com:80")
		if command==0:
			print ("Deleting database 1 (Bookings/penalties/missing)")
			url="http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel, self.api_key)
			try:
				conn.request("DELETE", url)
				response = conn.getresponse()
				confirm= "Database reset complete. Status {} {}"
				print(confirm.format(response.status, response.reason))
				conn.close()
			except:
				print ("connection failed")
			return "Database 1 reset complete"
		elif command==1 :
			print ("Deleting database 2 (prices)")
			url="http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel2, self.api_key)

			try:
				conn.request("DELETE", url)
				response = conn.getresponse()
				confirm= "Database reset complete. Status {} {}"
				print(confirm.format(response.status, response.reason))
				conn.close()
			except:
				print ("connection failed")
			return "Database 2 reset complete"
		elif command==2 :
			print ("Deleting dashboard")
			url="http://api.thingspeak.com/channels/%s/feeds.json?api_key=%s" % (self.channel3, self.api_key)

			try:
				conn.request("DELETE", url)
				response = conn.getresponse()
				confirm= "Database reset complete. Status {} {}"
				print(confirm.format(response.status, response.reason))
				conn.close()
			except:
				print ("connection failed")
			return "DASHBOARD reset complete"


	def catalog(self):
		"""docstring for alive"""
		url=self.URL_Catalogue+"/user"
		parameters={"username":"thingspeak"}
		parameters=json.dumps(parameters)
		x=requests.post(url,data=parameters)
		print("Connection to the catalogue status:")
		print(x.status_code)

if __name__ == '__main__':
	URL_base=''
	catalogue_port=''
	WM=''
	key=''
	channel=''
	key2=''
	channel2= ''
	key3=''
	channel3= ''
	api_key= ''

	try:
		file=open("./config.json")
		settings=json.loads(file.read())
		URL_base=		settings["URL_Base"]
		URL_Pi=         settings["URL_Pi"]
		catalogue_port=	settings["catalogue_port"]
		WM=				settings["washing_machines"]
		key=			settings["key"]
		channel= 		settings["channel"]
		key2=			settings["key2"]
		channel2=		settings["channel2"]
		key3=			settings["key3"]
		channel3=		settings["channel3"]
		api_key=		settings["api_key"]
		file.close()
	except:
		print("Configuration file error.")

	URL_catalogue=str(URL_Pi)+str(catalogue_port)

	print("Url catalogue= ",URL_catalogue,"\nNumber of WM= ",WM,"\nChannel 1 (key/channel)= ",key,channel,"\nChannel 2 (key/channel)= ",key2,channel2,"\nChannel 3 (key/channel)= ",key3,channel3,"\napi key= ",api_key)

	TSservice=thingspeakService(WM,key,channel,key2,channel2,key3,channel3,api_key,URL_catalogue)

	#	#Catalogue connection (POST)	
	try:	
		TSservice.catalog()
	except:
		print("Error while registering to catalogue")
	

	conf={
		'/':{
				'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
				'tools.sessions.on':True,
		}
	}		
	
	cherrypy.tree.mount(TSservice,'/thingspeakservice',conf)
	cherrypy.engine.start()
	cherrypy.engine.block()		
