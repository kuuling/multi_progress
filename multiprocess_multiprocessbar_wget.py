#coding:utf-8
#@update:2016-12-09 11:38:15
#@problem:sometimes mix print;curval less than real file size(even add TIME_SENSITIVE)
#@ref:https://github.com/aaren/multi_progress
#sudo pip install progressbar
#https://github.com/niltonvolpato/python-progressbar

import os,sys
import time,signal,urllib2
from blessings import Terminal
from progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar
def sign_int_handler(signum, frame):
    _globals = frame.f_globals
    if "pool" in _globals and hasattr(_globals["pool"], "terminate"):
        _globals["pool"].terminate()

    if signum == signal.SIGINT:
        os.kill(os.getpid(), signal.SIGKILL)    
signal.signal(signal.SIGINT, sign_int_handler)
term = Terminal()

#with term.fullscreen():
    #print('xxsdfsd%s'%term.location)
    #with term.location(0,1):
        #print("11dxxxxxxdfxxxxx11\r")
        #print("222asdfdfdsf\r")
    #with term.location(0,1):
        #time.sleep(1)
        #print("222asdfdfdsf\r")
#time.sleep(5)
#sys.exit()

class MultiProgressBar(object):
    """
    @ref:https://github.com/aaren/multi_progress
    [1,3,5]
    0==>1
    1==>3
    2==>5
    """
    def __init__(self,*args,**kwargs):
        class Title(Percentage):
            def update(self, mp):
                mp.stream.write('****Total:%s|Done:%s|Cur:%s\r' %(mp.max_task_num,mp.done,len(mp.processbars)))          
        self.stream = kwargs.setdefault("stream",sys.__stdout__)
        self.multi = kwargs.pop("multi",1)
        self.max_task_num = kwargs.pop("max_task_num",0)
        self.done = kwargs.pop("max_task_num",0)
        self.summary_pbar = kwargs.pop("summary_pbar",Title())
        self.summary_pbar_line_num = kwargs.pop("summary_pbar_line_num",-1)
 
        self.term = Terminal(**kwargs)
        #self.term = Terminal()
        if self.term.height:#some return None
            if self.summary_pbar_line_num < 0:
                self.summary_pbar_line_num = self.term.height - self.summary_pbar_line_num
        self.processbars = []

    def find(self,processbar):
        for index,val in enumerate(self.processbars):
            if processbar is val:
                return index
        else:
            return 0
    def realY(self,y):
        if y*self.multi < self.summary_pbar_line_num:
            return y*self.multi
        else:
            return (y+ self.summary_pbar_line_num)*self.multi     

    def start(self,processbar,*args,**kwargs):
        #if not self.processbars:
            #with self.term.location(0,0):
                #if self.term.height:
                    #print('\r'*self.term.height)
                #else:
                    #print('\r')
        if processbar not in self.processbars:
            processbar.fd = self.stream
            self.processbars.append(processbar)
        x = kwargs.pop('x',0)
        y = kwargs.pop('y',self.realY(self.find(processbar)))   
        with self.term.location(x,y):
            #print(y)
            processbar.start(*args,**kwargs)

    def update(self,processbar,*args,**kwargs):
        with self.term.location(0,self.summary_pbar_line_num):
            self.summary_pbar.update(self)
        x = kwargs.pop('x',0)
        y = kwargs.pop('y',self.realY(self.find(processbar)))   
        with self.term.location(x,y):
            processbar.update(*args,**kwargs)
    
    def finish(self,processbar,*args,**kwargs):
        x = kwargs.pop('x',0)
        y = kwargs.pop('y',self.realY(self.find(processbar.currval)))   
        if processbar in  self.processbars:
            self.processbars.remove(processbar)
            self.done+=1
            
        with self.term.location(x,y):
            #processbar.finish(*args,**kwargs) 
            processbar.finished = True
            processbar.update(self.maxval)
            #self.fd.write('\n')

     

class FileStatus(Percentage):
    'Displays the current percentage as a number with a percent sign.'
    TIME_SENSITIVE = True
    
    def update(self, pbar):
        return '[%s/%s]%3d%%' %(pbar.currval,pbar.maxval,pbar.percentage())

class WgetSpeedBar(ProgressBar):
    """ 
    #pbar = WgetSpeedBar()
    ##time.sleep(5)
    #pbar.start()
    #for i in range(100):
        #time.sleep(0.1)
        #pbar.update(i)
    #pbar.finish()
    #if self.currval > self.maxval
    #ValueError: Value out of range
    """
    def __init__(self,**kwargs):
        """  
        def __init__(self, maxval=None, widgets=None, term_width=None, poll=1,
            left_justify=True, fd=sys.stderr):
        """
        key = kwargs.pop("key","Unknown")
        kwargs.setdefault("widgets", None) 
        kwargs.setdefault("maxval",100)
        kwargs.setdefault("left_justify",True)
        kwargs.setdefault("fd",sys.stderr)
        #like sample1
        if kwargs["widgets"] == None:
            kwargs["widgets"] = ['%s: '%key, FileStatus(), "",
                            Bar(marker='#', left='[', right=']', fill_left=True ),
                            ' ', ETA(), ' ', FileTransferSpeed(),
                            ]        

        super(WgetSpeedBar,self).__init__(**kwargs)


#pbar = WgetSpeedBar()
##time.sleep(5)
#pbar.start()
#for i in range(100):
    #time.sleep(0.1)
    #pbar.update(i)
#pbar.finish()


def download(mp):     
    url = "http://dlsw.baidu.com/sw-search-sp/soft/e6/25282/python-2.7.6.amd64.1394777203.msi"
    url = "http://dlsw.baidu.com/sw-search-sp/soft/bc/27609/wrar510b4sc.1401936136.exe"
    rep = urllib2.urlopen(url,timeout=10)
    info = rep.info()
    key_words = {}
    file_all = 'tmp.%s.ts'%time.time()
    file_name = os.path.basename(file_all)
    log = '%s.log'%file_name
    key_words["key"] = file_name
    key_words["maxval"] = int(info["Content-Length"])
    #key_words["fd"] = open(log, mode='w', buffering=0)
    pbar = WgetSpeedBar(**key_words)
    with open( file_all, 'ab',buffering=0) as fp:
        mp.start(pbar)
        while True:
            try:
                if rep:
                    data = rep.next()
                    mp.update(pbar,int(pbar.currval+len(data)))
                    fp.write(data)
                    #fp.flush()
                    #print(len(data))
                    #time.sleep(3)

                else:
                    mp.finish(pbar)
                    break                    
            except StopIteration:
                if pbar.maxval == pbar.currval:
                    mp.finish(pbar)
                else:
                    time.sleep(pbar.poll)
                    mp.update(pbar)
                break
                
    
from multiprocessing import dummy
pool = dummy.Pool(3)
tnum = 10
mp = MultiProgressBar(**{"max_task_num":tnum})
with mp.term.fullscreen():
    for i in range(tnum):
        time.sleep(1)
        #https://segmentfault.com/a/1190000004172444
        #http://stackoverflow.com/a/1408476/6493535
        pool.apply_async(download,args=(mp,))
    pool.close()
    #pool.join()
    #def join(self):
    pool._worker_handler.join(sys.maxint)
    pool._task_handler.join(sys.maxint)
    pool._result_handler.join(sys.maxint)
    for p in pool._pool:
        p.join()

print(mp.summary_pbar.update(mp))
