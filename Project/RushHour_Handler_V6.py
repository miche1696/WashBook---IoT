import cherrypy	
import json
import time 
import requests 
import threading 
from datetime import datetime


class pricing(object):
	"""docstring for """
	exposed=True
	def __init__(self,url_1,url,rush_threshold,percentage,cost,url_pi,catalog_port):

		self.url_1=				url_1
		self.url=				url
		self.rush_threshold=	rush_threshold
		self.rush_threshold=round(self.rush_threshold)
		self.percentage=		percentage
		self.cost=				cost
		self.url_pi=			str(url_pi)
		self.catalog_port=catalog_port
		thing={"username":"RushHour_Handler"}
		thing=json.dumps(thing)
		url=self.url_pi+self.catalog_port+"/user"
		alive=requests.post(url,data=thing)
		

	def GET(self,*uri):

		var=list(uri)[0]
	
		if var=='1':
			print(var)
			prices=[]
			machine=[]
			for day in range (1,8):
				for hour in range (0,24):
					print (f"day {day} hour {hour} ")
					print("getting the booking info...")
					try:
						url1=self.url_1+f"1&hour={hour}&day={day}"
						check=requests.get(url1)
						check=check.content
						A=json.loads(check)
						L=len(A)						
						machine.append(L)

					except:
						output={"error retrieving data"}
						return output
					#4 to add information about the price of a slot
					# 	Example 				http://localhost:8080/thingspeakservice?command=4
					#	Example body			{"value" : "2,1,4"}			->		[Price,hour,day]
					
					price=self.cost
					if L<rush_threshold:
						price=price*(1-self.percentage/100)
						price=round(price,1)
					
					elif L==rush_threshold:
						price=self.cost
					
					elif L>rush_threshold:
						price=price*(1+self.percentage/100)
						price=round(price,1)
						
					else:
						print("length of machine list didnt match any rush_threshold")						
					price=price*100
					prices.append(price)
					
					print(price)
					
			pricing={"value":prices}
			print (pricing)
			pricing=json.dumps(pricing)
			url2=self.url_1+"4"
			post=requests.post(url2,data=pricing)
			
			plots={"value":machine}
			print (plots)
			plots=json.dumps(plots)		
			url3=self.url_1+"5"
			post_1=requests.post(url3,data=plots)
			
			### extra posts for the timeout ####	
			url_2=self.url_1+"6"	
			post_2=requests.post(url_2,data=plots)
			
			url_3=self.url_1+"7"
			post_3=requests.post(url_3,data=plots)
		
			return {"Hour prices has been filled and plots have been sent"}

if __name__=="__main__":
	
	try:
		file=open("config.json",'r')
		data=json.loads(file.read())
		url=					data["URL_Base"]	
		url_1=					data["URL_thingSpeak"]
		url_pi=					str(data["URL_Pi"])
		RushHour_Handler_port=	data["RushHour_Handler_port"]
		rush_threshold=			data["rush_hour_threshold"]
		percentage=				data["percentage"]
		cost=					data["cost"]
		catalog_port=           str(data["catalogue_port"])
		file.close()
	
	except:
		out={"error opening the config file in rush hour handler"}
		print(out)

	conf={
		'/':{
				'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
				'tools.sessions.on':True
		}
	}		
	cherrypy.tree.mount(pricing(url_1,url,rush_threshold,percentage,cost,url_pi,catalog_port),'/',conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port':RushHour_Handler_port})
	cherrypy.engine.start()
	cherrypy.engine.block()