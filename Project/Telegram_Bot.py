# -*- coding: UTF8 -*-
import requests
import datetime
import json


class BotHandler:
    def __init__(self, token):
            self.token = token
            self.api_url = "https://api.telegram.org/bot{}/".format(token)

    #url = "https://api.telegram.org/bot<token>/"

    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update

f=open("config.json", "r")
contents =f.read()
contents=json.loads(contents)
token = contents["telegram_token"] #Token of your bot
f.close()
magnito_bot = BotHandler(token) #Your bot's name


def main():
    URL_Base=contents["URL_Base"]
    scheduling_port=str(contents["scheduling_port"])
    new_offset = 0
    print('Bot Ready to Receive Inputs')
    while True:
        all_updates=magnito_bot.get_updates(new_offset)
        if len(all_updates) > 0:
            for current_update in all_updates:
                print(current_update)
                first_update_id = current_update['update_id']
                if 'text' not in current_update['message']:
                    first_chat_text='New member'
                else:
                    first_chat_text = current_update['message']['text']
                first_chat_id = current_update['message']['chat']['id']
                if 'first_name' in current_update['message']:
                    first_chat_name = current_update['message']['chat']['first_name']
                elif 'new_chat_member' in current_update['message']:
                    first_chat_name = current_update['message']['new_chat_member']['username']
                elif 'from' in current_update['message']:
                    first_chat_name = current_update['message']['from']['first_name']
                else:
                    first_chat_name = "unknown"




                print("Input Received")
                inputs=first_chat_text.split()



##########################################################

                if inputs[0]=="1":
                    if len(inputs)!=2:
                        output="Please input all necessary elements: '1 day'"
                    elif not inputs[1].isdigit():
                        output="Please input the day as a number between 1 and 7"
                    elif int(inputs[1])>7 or int(inputs[1])<1:
                        output="Please input day between 1 and 7"
                    else:
                        link=URL_Base+scheduling_port+"/"+inputs[0]+"?day="+inputs[1]
                        try:
                            response=requests.get(link)
                            body=response.content
                            body=json.loads(body)
                            output="Available Hours are: "+body["hours"]+" On day "+inputs[1]
                            print(output)
                        except:
                            output="A problem has occured, please contact maintenance"
                            print(output)


##########################################################


                elif inputs[0]=="2":
                    if len(inputs)!=4:
                        output="Please input all necessary elements: '2 room day hour'"
                    elif not inputs[1].isdigit() or not inputs[2].isdigit() or not inputs[3].isdigit():
                        output="Please input as numbers: '2 room day hour'"
                    elif int(inputs[2])>7 or int(inputs[2])<1:
                        output="Please input day between 1 and 7"
                    elif int(inputs[3])>23 or int(inputs[3])<0:
                        output="Please input an hour between 0 and 23"
                    else:
                        try:
                            link=URL_Base+scheduling_port+"/"+inputs[0]+"?room="+inputs[1]+"&day="+inputs[2]+"&hour="+inputs[3]
                            response=requests.get(link)
                            body=response.content
                            body=json.loads(body)
                            output="On day:"+str(body["day"])+" on hour:"+str(body["hour"])+", the price is:"+str(round(body["price"], 2))+" euro. You also have a penalty of: "+str(body["penalty"])+" euro."
                            print(output)
                        except:
                            output="A problem has occured, please contact maintenance"
                            print(output)
##########################################################



                elif inputs[0]=="3":
                    if len(inputs)!=4:
                        output="Please input all necessary elements: '3 room day hour'"
                    elif not inputs[1].isdigit() or not inputs[2].isdigit() or not inputs[3].isdigit():
                        output="Please input the numbers: '3 room day hour'"
                    elif int(inputs[2])>7 or int(inputs[2])<1:
                        output="Please input day between 1 and 7"
                    elif int(inputs[3])>23 or int(inputs[3])<0:
                        output="Please input an hour between 0 and 23"
                    else:
                        try:
                            link=URL_Base+scheduling_port+"/"+inputs[0]+"?room="+inputs[1]+"&day="+inputs[2]+"&hour="+inputs[3]
                            response=requests.get(link)
                            body=response.content
                            body=json.loads(body)
                            output="Booking: "+str(body["status"])+" on Machine: "+str(body["Machine"])+" for room: "+inputs[1]+" on day: "+str(body["day"])+" on hour: "+str(body["hour"])+", for: "+str(round(body["price"], 2))+" euro. You also have a penalty of: "+str(body["penalty"])+" euro."
                            print(output)
                        except:
                            output="A problem has occured, please contact maintenance"
                            print(output)
                

##########################################################


                elif inputs[0]=="2":
                    if len(inputs)!=4:
                        output="Please input all necessary elements: '2 room day hour'"
                    elif not inputs[1].isdigit() or not inputs[2].isdigit() or not inputs[3].isdigit():
                        output="Please input as numbers: '2 room day hour'"
                    elif int(inputs[2])>7 or int(inputs[2])<1:
                        output="Please input day between 1 and 7"
                    elif int(inputs[3])>23 or int(inputs[3])<0:
                        output="Please input an hour between 0 and 23"
                    else:
                        try:
                            link=URL_Base+scheduling_port+"/"+inputs[0]+"?room="+inputs[1]+"&day="+inputs[2]+"&hour="+inputs[3]
                            response=requests.get(link)
                            body=response.content
                            body=json.loads(body)
                            output="On day:"+str(body["day"])+" on hour:"+str(body["hour"])+", the price is:"+str(round(body["price"], 2))+" euro. You also have a penalty of: "+str(body["penalty"])+" euro."
                            print(output)
                        except:
                            output="A problem has occured, please contact maintenance"
                            print(output)
##########################################################


##########################################################




                elif inputs[0]=="/start":
                	output="Welcome to the WashBook Bot. \nTo check available hours in a certain date, please input: '1 day'\nTo check price of booking at a specific hour and your penalty: '2 room day hour'\nTo perform a booking, please input: '3 room day hour' \n Day=1...7 & Hour=0...23"
                


##########################################################




                else:
                	output="Please Select a Valid Method According to Instructions, to review instructions type /start"
                try:
                    magnito_bot.send_message(first_chat_id, output)
                    new_offset = first_update_id + 1
                except:
                    print("Returning Message to Telegram Failed")


##########################################################


if __name__ == '__main__':
    print('Starting Telegram Bot')
    try:
        file=open("./config.json")
        settings=json.loads(file.read())
        URL_Pi=         str(settings["URL_Pi"])
        catalogue_port= str(settings["catalogue_port"])
        file.close()
    except:
        print("Problem in configuration file")
    try:
        print("Registering in Catalog")
        thing={"username":"Telegram_bot"}
        thing=json.dumps(thing)
        alive=requests.post(URL_Pi+catalogue_port+"/user",data=thing)
        print("Registered in catalog successfuly")
    except:
        print("Error connecting to catalog")
    try:
        main()
    except:
        print("A problem has occured in main function...exiting program")
        exit()