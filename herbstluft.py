import subprocess
import threading

mod1='Mod1+'
mod4='Mod4+'
control='Ctrl+'
shift='Shift+'
enter='Return'
tab='Tab'
left='Left'
right='Right'
up='Up'
down='Down'

class HerbstluftClient(object):
    #execute the command
    def do_command(self,command):
        try:
            hc_output=subprocess.check_output(['herbstclient']+command.split(' '))
        except CalledProcessError as e:
            hc_output=e.output
            print('herbstclient returned '+str(e.returncode))

        return hc_output
        #subprocess.call(['herbstclient']+command.split(' '))

    #keybinding commands
    def keybind(self,key,command):
        self.do_command('keybind '+key+' '+command)
    def keyunbind(self,key):
        command='keyunbind '
        if 'all'==key:
           command+='--all'
        else:
            command+=key
        self.do_command(command)

    #mousebinding commands
    def mousebind(self,key,command):
        self.do_command('mousebind '+key+' '+command)
    def mouseunbind(self,key):
        command='mouseunbind '
        if 'all'==key:
            command+='--all'
        else:
            command+=key
        self.do_command(command)

    #hook stuff
    def emit_hook(self,hook):
        self.do_command('emit_hook '+hook)

    #locking,unlocking speeds things up by disabling paints
    def lock(self):
        self.do_command('lock')
    def unlock(self):
        self.do_command('unlock')

    #tag stuff
    def add(self,tag):
        self.do_command('add '+tag)
    def use(self,tag):
        self.do_command('use '+tag)
    def use_index(self,index):
        self.do_command('use_index '+str(index))
    def use_previous(self):
        self.do_command('use_previous')
    def merge_tag(self,tag,target=''):
        self.do_command('merge_tag '+tag+' '+target)
    def rename(self,old_tag,new_tag):
        self.do_command('rename '+old_tag+' '+new_tag)
    def move(self,tag):
        self.do_command('move '+tag)
    def move_index(self,index):
        self.do_command('move_index '+str(index))
    def tag_status(self,monitor=''):
        return self.do_command('tag_status '+str(monitor)).split()

    #skipping lock and unlock for tags for now
    #will do multimonitor stuff later
    
    #attribute stuff
    def attr(self,path='',new_value=''):
        if '' != path:
            path = ' ' + path
        if '' != new_value:
            new_value =' ' + str(new_value)
        return self.do_command('attr'+path+new_value)
    def get_attr(self,attribute):
        return self.do_command('get_attr '+attribute)
    def set_attr(self,attribute,new_value):
        self.do_command('get_attr '+attribute+' '+str(new_value))

    #get/set/toggle name value pairs
    def set(self,name,value):
        self.do_command('set '+name+' '+str(value))
    def get(self,name):
        return self.do_command('get '+name)

    #rules
    def unrule(self,label):
        command='unrule '
        if 'all'==label:
           command+='--all'
        else:
            command+=label
        self.do_command(command)
    def rule(self,rule):
        self.do_command('rule '+rule)

    #monitor stuff
    def monitor_rect(self,monitor=0,with_pad=True):
        #return [x,y,w,h]
        command='monitor_rect '
        if False==with_pad:
            command+='-p '
        command+=str(monitor)
        rect=self.do_command(command)
        return rect.split()
    def pad(self,monitor,pad_up=0,pad_right=0,pad_down=0,pad_left=0):
        command='pad '
        command+=str(monitor)+' '
        command+=str(pad_up)+' '
        command+=str(pad_right)+' '
        command+=str(pad_down)+' '
        command+=str(pad_left)
        self.do_command(command)
    def list_padding(self,monitor=''):
        return self.do_command('list_padding '+str(monitor)).split()

class HerbstluftChain(HerbstluftClient):
    command_chain=''
    separater=' .-. '
    def __enter__(self):
        self.command_chain=''
        return self

    def __exit__(self,type,value,traceback):
        super(HerbstluftChain,self).do_command('chain'+self.command_chain)

    def do_command(self,command):
        self.command_chain+=self.separater+command

class HerbstluftTimer(threading.Thread):
    def __init__(self,seconds=5):
        super(HerbstluftTimer,self).__init__()
        self.sleep_length=seconds
        self.event=threading.Event()

    def run(self):
        hc = HerbstluftClient()
        while True != self.event.wait(self.sleep_length):
            hc.emit_hook('timer_event')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self,type,value,traceback):
        self.event.set()
        self.join()
