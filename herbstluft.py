import subprocess

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
        subprocess.call(['herbstclient']+command.split(' '))

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
    #skipping lock and unlock for tags for now
    #will do multimonitor stuff later
    
    #get/get/toggle name value pairs

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

