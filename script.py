import web,re,traceback,sys
import time

urls=(
"/","displaythreads",
"/viewthread","displaythreads",
"/viewthread/(.*)/Vote/(Up|Down)","vote",
"/viewthread/(.*)","displaythread",
"/newthread/(.*)","newthread",
"/newthread","newthread",
'/(.*)','autoretrieve'
)

def log(message=None):
    sys.stderr.write("\t"+message+"\n")
    logf = open("Action Log",'a')
    logf.write(message)
    logf.close()
entries={}###{entryname:{property:value}}
class displaythread():
    template=web.template.frender("Thread Viewer Template.html")
    def GET(self,name):
        try:
            entry=entries[name]
        except KeyError:
            log("Invalid name")
            return "401"
        print entry['replies']
        try:
            percent = entry['votes']/entry['totvotes']
        except ZeroDivisionError:
            percent = 50;log("*Zero total votes")
        return self.template(
            name,
            len(entries)-1,
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
            return self.template(mode)
        if threadname in entries:
            return self.template("Exists")
        entries[threadname]={"creator":username,"votes":0,"totvotes":0,"replies":[],"creatorname":[]}
        raise web.seeother("/viewthread/"+threadname)
class displaythreads:
    template=web.template.frender('Thread Template.html')
    def GET(self):
        return self.template(
            len(entries),
            [value['creator'] for value in entries.values()],
            entries.keys(),
            [value['votes'] for value in entries.values()],
            [value['totvotes'] for value in entries.values()]
                      )
class vote:
    template=web.template.frender('vote.html')
    def GET(self,thread,vote):
        try:
            current=web.cookies().get("vote_"+thread)
        except:
            current="BEING DELETED" #act like it is being deleted if its not there.
        ######Set cookies and change votes#########
        ##Removing/Adding an extra vote if it was previously voted the other way##
        if vote=="Up":
            web.setcookie("Voted:"+thread,"up")
            if current=="down":
                entries[thread]["votes"]+=1
            entries[thread]["votes"]+=1
            ID=0
        elif vote=="Down":
            web.setcookie("Voted:"+thread,"down")
            if current=="up":
                entries[thread]["votes"]-=1
            entries[thread]["votes"]-=1
            ID=0
        elif vote=="Remove":
            if current=="up":
                entries[thread]["votes"]-=1
            elif current=="down":
                entries[thread]["votes"]+=1
            web.setcookie("Voted:"+thread,"BEING DELETED",expires=1)
            totvotes-=1
            ID=1
        if current == "BEING DELETED":# if he hasn't already voted, increase the total vote count by 1
            totvotes+=1
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
