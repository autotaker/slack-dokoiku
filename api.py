import os, time
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import codecs
import json
import websockets
import asyncio
from io import StringIO

class APIError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return msg

def check_json(value):
    if isinstance(value, dict):
        if value.get("ok") is True:
            return True 
    return False 

class RTMAPI:
    def __init__(self,ret):
        self.users = dict([ (user["id"] , user) for user in ret["users"] ])
        self.channels = dict([ (channel["id"] , channel) for channel in ret["users"] ])
        self.msg_ident = 1
    
    def get_user_name(self, user_id):
        self.users[user_id]["name"]

    def find_user_id(self, username):
        for user in values(self.users):
            if user.name == username:
                return user["id"]
        return None
    def get_channel_name(self, channel_name):
        self.channels[channel_id]["name"]

    def find_channel_id(self, channelname):
        for channel in values(self.channels):
            if channel.name == channelname:
                return channel["id"]
        return None

    def identify(self, data):
        data["id"] = self.msg_ident
        self.msg_ident += 1
        return data
    
    def send_message_rtm(self, message, channel='bottest', channel_id=None):
        if channel_id is None:
            channel_id = find_channel_id(self, channel)
        if channel_id:
            return self.identify({ "type": "message",
                                   "channel": channel_id,
                                   "text": message })
        else:
            raise APIError("invalid channel: {}".format(channel))

class API:
    def __init__(self):
        if "SLACK_API_TOKEN" in os.environ:
            self.token = os.environ["SLACK_API_TOKEN"]
        else:
            raise APIError("environtment variable SLACK_API_TOKEN is unset")
    def open_url(self, url, params):
        params["token"] = self.token
        data = urllib.parse.urlencode(params)
        data = data.encode('ascii')
        try:
            with urllib.request.urlopen(url, data) as response:
                reader = codecs.getreader("utf-8")
                value = json.load(reader(response))
                if check_json(value):
                    return value
                else:
                    raise APIError("Response Error: " + repr(value))
        except HTTPError as e:
            raise APIError("Couldn't send the message. Reason: HTTPError: " + e.code)
        except URLError as e:
            raise APIError("Couldn't send the message. Reason: URLError: " + e.reason)
    def send_message(self, message, channel="#bottest"):
        params = { "channel": channel, 
                   "as_user": "true",
                   "text": message }
        url = "https://slack.com/api/chat.postMessage"
        ret = self.open_url(url, params)
        print(ret)


    def listen(self, handler):
        ret = self.open_url("https://slack.com/api/rtm.start", { "no_unreads": "true"})
        url = ret["url"]
        rtm = RTMAPI(ret)
        async def hello():
            async with websockets.connect(url) as websocket:
                ident = 0
                while True:
                    event = await websocket.recv()
                    event = json.loads(event)
                    if "reply_to" in event:
                        print(event)
                        continue
                    elif event["type"] == "error":
                        return 
                    try:
                        res = handler(rtm, event)
                        if res:
                            print("Send: {}".format(res))
                            await websocket.send(json.dumps(res))
                            time.sleep(5)
                    except Exception as e:
                        print("Error!")
                        print(e)
                        pass
                    
        asyncio.get_event_loop().run_until_complete(hello())

if __name__ == '__main__':
    try:
        api = API()
        # api.send_message("ほげ")
        api.listen(handler)

    except APIError as e:
        print("Error:", e.message)
