from api import *
import time, os
from websockets.exceptions import ConnectionClosed
from capture import *
import asyncio

capture_busy = False

def sakana_capture(channel):
    global capture_busy
    if capture_busy:
        return 'busy'
    async def capture_async():
        global capture_busy
        try:
            await capture('data/')
            os.system('./upload.sh {} {}'.format('data/capture.mp4', channel))
        finally:
            capture_busy = False
    capture_busy = True
    asyncio.ensure_future(capture_async())
    return 'capturing'
    

def sakana(cmd, event, rtm):
    cmd = cmd.split()
    if len(cmd) == 0:
        return None
    if cmd[0] != 'sakana':
        return None
    return sakana_capture(event["channel"])

def handler(rtm, event):
    if event["type"] == "message" and 'bot_id' not in event:
        msg = event["text"]
        print("Message({})".format(repr(event["text"])))
        ret = sakana(msg, event, rtm)
        if ret:
            print(ret)
            return rtm.send_message_rtm(ret, 
                                        channel_id = event["channel"])
        return None
def main():
    api = API()
    api.send_message('sakana is alive')
    try:
        retryCount = 0
        while retryCount < 10:
            t1 = time.time()
            try:
                api.listen(handler)
            except ConnectionClosed:
                pass
            t2 = time.time()
            print("[%.0f] Connection Closed. Try recconect(%d)" % (t2, retryCount))
            if t2 - t1 <= 10:
                retryCount += 1
            else:
                retryCount = 0
    finally:
        api.send_message('sakana is dead')

def test():
    pass

if __name__ == '__main__':
    try:
        main()
    except APIError as e:
        print("Error:", e.message)

