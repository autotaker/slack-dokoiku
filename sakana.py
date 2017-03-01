from api import *
import time, os
from websockets.exceptions import ConnectionClosed

def sakana_capture():
    os.system('./upload.sh {}'.format('sample.mp4'))

def sakana(cmd):
    cmd = cmd.split()
    if len(cmd) == 0:
        return None
    if cmd[0] != 'sakana':
        return None
    return sakana_capture()

def handler(rtm, event):
    if event["type"] == "message" and 'bot_id' not in event:
        msg = event["text"]
        print("Message({})".format(repr(event["text"])))
        ret = sakana(msg)
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

