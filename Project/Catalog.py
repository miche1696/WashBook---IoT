#######################################################################################################################
#
#                                             GENERAL PURPOSE CATALOG
#
#######################################################################################################################

#######################################################################################################################
# Library section
import json
import cherrypy
import threading
import time

#######################################################################################################################
# Class for the web service

class Catalog(object):
    exposed=True
    def __init__(self):
        self.broker ={'ID': '192.168.1.9', 'port': 1883}
        self.token ={'token': '681759966:AAF7xH6JYtBcyju7Sgzku9MYaKjAIx2g6hM'}
        # This part reads the file in which there are the information about device(s) and user(s) already registered in the catalog
        # If the file is empty (first use of the catalog) the class variables are initialized as empty lists.
        # NOTE: For the first use of the program the files must be initialized as []
        device_file = open('device.json', 'r')
        self.device = json.loads(device_file.read())
        device_file.close()

        user_file = open('user.json', 'r')
        self.user = json.loads(user_file.read())
        user_file.close()
        
    def read_user(self, user=True, read=True):
        if not user and read:
            device_file = open('device.json', 'r')
            self.device = json.loads(device_file.read())
            device_file.close()
        elif user and read:
            user_file = open('user.json', 'r')
            self.user = json.loads(user_file.read())
            user_file.close()
        elif not user and not read:
            device_file = open('device.json', 'w')
            device_file.write(json.dumps(self.device))
            device_file.close()
        elif user and not read:
            user_file = open('user.json', 'w')
            user_file.write(json.dumps(self.user))
            user_file.close()            

    # The method GET retrieves information about the registered users and devices in JSON format
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def GET(self, *uri, **params):

        if uri[0] == 'token':
            return self.token

        if uri[0] == 'broker':
            return self.broker
        
        if uri[0] == 'device':
            self.read_user(False,True)
            if params['ID']=='all':
                return self.device
            else:
                for dev in self.device:
                    if params['ID'] == dev['ID']:
                        return dev
                return {'ID': None}

        if uri[0] == 'user':
            self.read_user()
            if params['username']=='all':
                return self.user
            else:
                for user in self.user:
                    if params['username'] == user['username']:
                        return user
                return {'username': None}
                    

    # The method POST adds new device and user to the list. It also keeps updated the files each time a new device or user is inserted.
    # There is also a control to verify that the ID of each user or device is unique. If the new user (or device) ID is equal to
    # another one already present in the list a status code 409 (conflict) is returned
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):

        if uri[0] == 'device':
            new_device=json.loads(cherrypy.request.body.read())
            new_device['time_stamp']=time.time()
            self.read_user(False,True)
            for dev in self.device:
                if dev['ID']== new_device['ID']:
                   return {"Request status": "Rejected", "Device status": "Already registered"}
        
            self.device.append(new_device)
            self.read_user(False,False)
            return {"Request status": "Accepted", "Device status": "Registered"}        

        if uri[0] == 'user':
            new_user=json.loads(cherrypy.request.body.read())
            self.read_user()
            for user in self.user:
                if user['username'] == new_user['username']:
                    return {"Request status": "Rejected", "User status": "Already registered"}
            
            self.user.append(new_user)
            self.read_user(True,False)
            return {"Request status": "Accepted", "User status": "Registered"}
            
    # The method PUT updates the timestamp of a device. The ID is passed through parameter in the URL.
    # If the ID is not present in the list a status code 400 (Bad request) is returned
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def PUT(self,*uri,**params):
        if uri[0] == 'device':
            self.read_user(False,True)
            for dev in self.device:
                if dev['ID'] == params['ID']:
                    dev['time_stamp'] = str(time.time())
                    self.read_user(False,False)
                    return {"Request status": "Accepted", "Device status": "Already present, timestamp updated"}
            
            return {"Request status": "Rejected", "Device status": "Not present, timestamp NOT updated"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def DELETE(self,*uri,**params):
        if uri[0]=='device':
            self.read_user(False,True)
            for dev in self.device:
                if dev['ID'] == params['ID']:
                    self.device.remove(dev)
                    self.read_user(False,False)
                    return {"Request status": "Accepted", "Device status": "Removed"}
                
            return  {"Request status": "Device not found", "Device status": "Not removed"}

        if uri[0]=='user':
            self.read_user()
            for us in self.user:
                if us['username'] == params['username']:
                    self.user.remove(us)
                    self.read_user(True,False)
                    return {"Request status": "Accepted", "User status": "Removed"}
                
            return  {"Request status": "User not found", "User status": "Not removed"}
        
#######################################################################################################################
# Class creation for the thread
# One thread for the web service and another one to remove the "old" device(s)
class thread_web(threading.Thread):

    def __init__(self,name):
        threading.Thread.__init__(self, name=name)

    def run(self):
        if __name__ == '__main__':
            
            file=open("config.json",'r')
            data=json.loads(file.read())    
            port=data["catalogue_port"]
            file.close()
            conf = {
                '/': {
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on': True,
                }
            }
        cherrypy.tree.mount(Catalog(), '/', conf)
        cherrypy.config.update({'server.socket_host': '0.0.0.0'})
        cherrypy.config.update({'server.socket_port': port})
        cherrypy.engine.start()
        cherrypy.engine.block()

class thread_delete(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self, name=name)
    	
    def run(self):

        while True:
            removed=False
            print('Searching for deleting...')
            device_file = open('device.json', 'r')
            dev_list = json.loads(device_file.read())
            for dev in dev_list:
                if (time.time()-float(dev['time_stamp']))>=120:
                    dev_list.remove(dev)
                    print ('Removed: ', dev)
                    removed=True

            device_file.close()

            if removed:
                print ('new device list: ', dev_list)
                device_file = open('device.json', 'w')
                device_file.write(json.dumps(dev_list))
                device_file.close()
            elif not removed:
                print ('Nothing to remove')
            time.sleep(60)

#######################################################################################################################
# Section to make run the threads
web=thread_web('web')
delete=thread_delete('delete')

web.start()
delete.start()
