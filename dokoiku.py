from api import *
import random
import sqlite3

conn = sqlite3.connect('db.sqlite')

def dokoiku_list(place = 'hongo'):
    c = conn.cursor()
    if place == 'all':
        res = c.execute("SELECT name FROM dokoiku")
    else:
        res = c.execute("SELECT name FROM dokoiku where place = ?", (place,))
    return list(map(lambda x: x[0],list(res)))

def dokoiku_choice(l = None, place='hongo'):
    if l is None:
        l = dokoiku_list(place)
    if len(l) == 0:
        return 'no candidates'
    return random.choice(l)

def dokoiku_show_list(place='all'):
    c = conn.cursor()
    if place == 'all':
        places = list(c.execute("SELECT DISTINCT place FROM dokoiku"))
    else:
        places = [(place,)]
    msg = ''
    for p in places:
        names = c.execute("SELECT name FROM dokoiku where place = ?", p)
        msg += "%10s: " % p + ' '.join(map(lambda x: x[0],names)) + '\n'
    return msg

def dokoiku_add(names, place):
    c = conn.cursor()
    for name in names:
        l = c.execute("SELECT * FROM dokoiku WHERE name = ? AND place = ?", (name, place))
        if len(list(l)) == 0:
            c.execute("INSERT INTO dokoiku(name,place) VALUES (?, ?)", (name, place))
    conn.commit()
    return 'added'

def dokoiku_delete(names, place):
    c = conn.cursor()
    if name[0] == 'all':
        c.execute("DELETE FROM dokoiku WHERE place = ?", (place,))
    else:
        for name in names:
            c.execute("DELETE FROM dokoiku WHERE name = ? AND place = ?", (name, place))
    conn.commit()
    return 'deleted'

usage_text="""usage:
    dokoiku [CAND]              # choose one from the given list
    dokoiku help                # show this message
    dokoiku list PLACE          # show candidates around PLACE
    dokoiku around PLACE        # choose one from the specified PLACE
    dokoiku add PLACE [NAME]    # register restaurants around PLACE
    dokoiku delete PLACE all    # unregister all restaurants around PLACE 
    dokoiku delete PLACE [NAME] # unregister the specified restaurants
"""

def dokoiku_help():
    return usage_text

def dokoiku(cmd):
    cmd = cmd.split()
    if len(cmd) == 0:
        return None
    if cmd[0] != 'dokoiku':
        return None
    if len(cmd) == 1:
        return dokoiku_choice()
    if   cmd[1] == 'help':
        return dokoiku_help()
    elif cmd[1] == 'list':
        if len(cmd) == 2:
            return dokoiku_show_list('all')
        else:
            return dokoiku_show_list(cmd[2])
    elif cmd[1] == 'add':
        if len(cmd) < 4:
            return 'invalid'
        place = cmd[2]
        names = cmd[3:]
        if place == 'all':
            return 'all is a reserved word'
        return dokoiku_add(names, place)
    elif cmd[1] == 'delte' or cmd[1] == 'del':
        if len(cmd) < 4:
            return 'invalid'
        place = cmd[2]
        names = cmd[3]
        return dokoiku_delete(names, place)
    elif cmd[1] == 'around':
        if len(cmd) != 3:
            return 'invalid'
        place = cmd[2]
        return dokoiku_choice(place = place)
    return dokoiku_choice(cmd[1:])

def handler(rtm, event):
    if event["type"] == "message" and 'bot_id' not in event:
        msg = event["text"]
        print("Message({})".format(repr(event["text"])))
        ret = dokoiku(msg)
        if ret:
            print(ret)
            return rtm.send_message_rtm(ret, 
                                        channel_id = event["channel"])
        return None
def main():
    api = API()
    api.send_message('dokoiku is alive')
    try:
        api.listen(handler)
    finally:
        api.send_message('dokoiku is dead')

def test():
    print(dokoiku('dokoiku help'))
    print(dokoiku('dokoiku list'))
    print(dokoiku('dokoiku add yamate hongo'))
    print(dokoiku('dokoiku add ichiban hongo'))
    print(dokoiku('dokoiku add tsuru roppongi'))
    print(dokoiku('dokoiku list'))
    print(dokoiku('dokoiku list hongo'))
    print(dokoiku('dokoiku list roppongi'))
    print(dokoiku('dokoiku delete hongo'))
    print(dokoiku('dokoiku list'))

if __name__ == '__main__':
    try:
        main()
    except APIError as e:
        print("Error:", e.message)

