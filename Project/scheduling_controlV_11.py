import cherrypy
import json
import time
import requests

class schedule(object):
	"""docstring for Booking"""
	exposed=True
	def __init__(self,wms,url,url1,scheduling_port,catalogue_port,cost,url_pi):
		self.url=url
		self.wms=wms
		self.url_1=url1
		self.scheduling_port=scheduling_port
		self.catalogue_port=catalogue_port
		self.cost=cost
		self.url_pi=url_pi
    #______ catalogue info_____:
		
		thing={"username":"scheduling"}
		thing=json.dumps(thing)
		cat_url=self.url_pi+f"{catalogue_port}/user"
		alive=requests.post(cat_url,data=thing)
		
	def GET(self,*uri,**params):
		var=list(uri)[0]	
		if var=='1':
			day=params["day"]
			output={"hours":[]}

			day=int(day)
			if day not in range(8):
				output={"wrong day is selected "}	
				return output	
			try:
				url1=self.url_1+f"4&day={day}"
				hour_check=requests.get(url1)
				
				avl_hrs=hour_check.content
				avl_hrs=json.loads(avl_hrs)
				output["hours"]=avl_hrs
				output=json.dumps(output)
				return output			
			except:
				output={"an error retrieving data occurred"}
				return output
####################_________ OPTION 2 The Booking________################################
		#booking info exmaple http://localhost:9090/2?room=15&day=5&hour=6
		if var=='2':
			day=params["day"]
			ID=params["room"]
			hour=params["hour"]

			output={"room":None,"penalty":None,"day":None,"hour":None,"price":None}
			try:
				url2=self.url_1+f"2&room={ID}"
				room_check=requests.get(url2)
				penalty=room_check.content
				penalty=json.loads(penalty)
				p=penalty[1]
				if p !=0:
					output["penalty"]=p
			except:
				output={"couldnt retrieve the penalty"}
				return penalty

			try:
				url3=self.url_1+f"3&hour={hour}&day={day}"
				price_check=requests.get(url3)
				percent=price_check.content
				percent=json.loads(percent)
				percent=percent/100
				
				print(percent)
				
				price=percent
				output["price"]=price
				output["day"]=day
				output["hour"]=hour
				output["room"]=ID

				output=json.dumps(output)
				return output
			except:
				output={"couldnt retrieve the hour price"}
				return penalty
		
		if var =='3':
			hour=params["hour"]			
			day=params["day"]
			ID=params["room"]			
			
			
			#---------------------------------------------------------------------
			###____ Day entry and control ____##
			day=int(day)
			if day not in range(8):
				output={"wrong day is selected "}	
				return output			
			#---------------------------------------------------------------------
			###____Hour  entry and control ____###	
			hour=int(hour)
			if hour not in range (24):
				output={"wrong hour was selected "}	
				return output
			
			url4=self.url_1+f"2&room={ID}"
			room_check=requests.get(url4)
			penalty=room_check.content
			penalty=json.loads(penalty)
			p=penalty[1]
			if p!=0:
				self.cost+=p		
			#---------------------------------------------------------------------
			#### THE GET part to check if machines are available ######
			url5=self.url_1+f"1&hour={hour}&day={day}"
			check=requests.get(url5)
			A=check.content
			A=json.loads(A)
			n=len(A)
			
			if n < self.wms:	#if so booking will happen:						
				url6=self.url_1+f"3&hour={hour}&day={day}"
				check=requests.get(f"http://localhost:8080/thingspeakservice?command=3&hour={hour}&day={day}")
				percent=check.content
				percent=json.loads(percent)
				percent=percent/100
				
					
				booking={"value":[ID,hour,day]}
				booking=json.dumps(booking)
				url7=self.url_1+"0"
				requests.post(url7,data=booking)
				rank=n+1					
				output={"day":day,"hour":hour,"price":percent,"penalty":p,"Machine":rank,"status":"success"}											
				output=json.dumps(output)
			else :
			
				output={"Requested hour is booked "}							
		else:
			output={"wrong html"}
		return output

if __name__=="__main__":
###____ config file data extraction____#####
	try:	
		file=open("config.json",'r')
		data=json.loads(file.read())
		wms=				data["washing_machines"]
		url=				data["URL_Base"]
		url_1=				data["URL_thingSpeak"]
		url_pi=				str(data["URL_Pi"])
		scheduling_port=	data["scheduling_port"]
		catalogue_port=		data["catalogue_port"]
		cost=				data["cost"]
		file.close()
	
	except:
		print("problem opening the file")

	conf={
		'/':{
				'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
				'tool.session.on':True
		}
	}		
	cherrypy.tree.mount(schedule(wms,url,url_1,scheduling_port,catalogue_port,cost,url_pi),'/',conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port':scheduling_port})
	cherrypy.engine.start()
	cherrypy.engine.block()

	