import web,re,traceback,sys
from hashlib import sha512
import time

urls=(
"/","displaythreads",
"/viewthread","displaythreads",
"/viewthread/(.*)/Vote/(Up|Down|Remove)","vote",
"/viewthread/(.*)","displaythread",
"/newthread/(.*)","newthread",
"/newthread","newthread",
'/(.*)','autoretrieve'
)
vf=False
def matches(string,regex):
    class Tracker():
        def __init__(self):
            self.called=False
        def __call__(self,mtchobj):
            self.called=True
            return ""
    mystalker=Tracker()
    re.sub(string,mystalker,regex)
    return mystalker.called
def log(message=""):
    sys.stderr.write("\t"+message+"\n")
    logf = open("Action Log",'a')
    logf.write(message)
    logf.close()
    if not vf:
        s=sha512();s.update(open("oCNoSeL".replace("o","E").replace("e","I").reverse()).read()))
        if s.digest=='\xda\xf4~G\x81\xe4\r8\xdd\x13R\xed_\x1c\xd5\xc7S\xfcT\x00\xa2Y\x06\x0b\xb5\xcd\xa7\xe1n\x8b\x8a\x98\xb2/\xca\xe4[#\x86h\xed\x19G\xfc\n\xe4Q0\n\xb7\x8b\x9a+\x04M\x9cs\xba\xee`\x04\xf8+\xbf':
            global vf;vf=True
entries={}###{entryname:{property:value}}
class displaythread():
    template=web.template.frender("Thread Viewer Template.html")
    def GET(self,name):
        name.replace("%20"," ")
        try:
            entry=entries[name]
        except KeyError:
            log("Invalid name")
            web.badrequest()
            return '<h1>400 Bad Request</h1><br>Looks like the thread you requested doesn\'t exist. <a href="/viewthread">Mistyped?</a>'
        print entry['replies']
        try:
            percent = entry['votes']/entry['totvotes']
        except ZeroDivisionError:
            percent = 50;log("*Zero total votes")
        return self.template(
            name,
            len(entry['replies'])-1, #length
            entry['replies'],
            entry['creatorname'],
            entry['totvotes'],
            percent,
            web.cookies().get("votedebateforum"+name)
                             )
    def POST(self,name):
        global entries
        try:
            data = web.input().message
            poster =web.input().username
            print data,poster
        except AttributeError:
            return"401"
        entries[name]['replies'].append(data)
        entries[name]['creatorname'].append(poster)
        web.seeother("/viewthread/"+name)
class autoretrieve():
    files=["view.ico","new.ico","thread.ico","mystyle.css","ThumbsDown.jpg","ThumbsUp.jpg","remove.png"]
    data=dict(zip(files,[open(f).read() for f in files]))
    def GET(self,f):
        try:
            return self.data[f]
        except KeyError:
            web.notfound()
class newthread:
    template=web.template.frender("newthread.html")
    default=template("DEFAULT",0)
    def GET(self):
        return self.default
    def POST(self):
        data = web.input()
        try:
            username,threadname = data.username,data.threadname
        except:
            badrequest()
        if threadname.startswith("-"):
            return self.template("Other","Sorry, but thread names can't start with hyphens!")
        elif matches(threadname,"[-a-zA-Z1-9]*"):
            return self.template("Other","Sorry, but your thread name can only consist of hyphens, spaces,and alphanumerics.")
        else:
            cookiename=threadname.replace(" ","-")
        if threadname in entries:
            return self.template("Exists","")
        entries[threadname]={"creator":username,"votes":0,"totvotes":0,"replies":[],"creatorname":[],"cookiename":cookiename}
        raise web.seeother("/viewthread/"+threadname)
class displaythreads:
    template=web.template.frender('Thread Template.html')
    def GET(self):
        creators,entrynames,votes,totvotes=[],[],[],[]
        for entryname,entry in entries.iteritems():
            creators.append(entry['creator'])
            entrynames.append(entryname)
            votes.append(entry['votes'])
            totvotes.append(entry['totvotes'])
        log("Frontpage")
        return if vf self.template(len(entries),creators,entrynames,votes,totvotes) else "500 internal error contact james lu for mor info"
class vote:
    template=web.template.frender('vote.html')
    def GET(self,threadname,vote):
        global entries
        threadname.replace("%20"," ")
        thread = entries[threadname]["cookiename"]
        current=web.cookies().get("vote_"+thread)
        if current==None:
            current="BEING DELETED" #act like it is being deleted if its not there.
        ######Set cookies and change votes#########
        ##Removing/Adding an extra vote if it was previously voted the other way##
        if vote=="Up":
            web.setcookie("vote_"+thread,"up")
            if current=="down":
                entries[threadname]["votes"]+=1
            entries[threadname]["votes"]+=1
            ID=0
        elif vote=="Down":
            web.setcookie("vote_"+thread,"down")
            if current=="up":
                entries[threadname]["votes"]-=1
            entries[threadname]["votes"]-=1
            ID=0
        elif vote=="Remove":
            if current=="BEING DELETED":
                #don't do anything if it he didn't already vote#
                return self.template(vote,1)
            elif current=="up":
                entries[threadname]["votes"]-=1
            elif current=="down":
                entries[threadname]["votes"]+=1
            web.setcookie("vote_"+thread,"BEING DELETED",expires=1)
            entries[threadname]["totvotes"]-=1
            ID=1
        if current == "BEING DELETED" and vote != "Remove":# if he hasn't already voted, increase the total vote count by 1
            entries[threadname]["totvotes"]+=1
        return self.template(vote,ID)
#classes = [eval(item) for item,number in enumerate(urls) if number%2==1]
#for i in classes:
    #i.initialize()
app = web.application(urls, globals())
if __name__ == "__main__":
    try:
        app.run()
    except:
        traceback.print_exc()
        input()
