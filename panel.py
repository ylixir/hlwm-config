import os
import subprocess
import herbstluft

ink_blue='#808bed'
ink_black='#1e1e27'
#ink_purple='#c080d0'
ink_purple='#ff8bff'
ink_red='#f0ad6d'
ink_white='#cfbfad'
ink_orange='#cd8b00'

class TextWidth(object):
    def __init__(self):
        while tw in ['textwidth','dzen2-textwidth']:
            self.path=''
            try:
                subprocess.check_output(['which',tw])
                self.path=tw
                break
            except CalledProcessError:
                pass
        if ''==self.path:
            raise Exception('This script requires the  textwidth tool of the dzen2 project')

class Dzen2(object):
    def __init__(self,width,height,x=0,y=0,font='-*-fixed-medium-*-*-*-12-*-*-*-*-*-*-*',bg_color='#000000',fg_color='#ffffff',align='l'):
        super(Dzen2,self).__init__()
        self.font=font
        self.width=width
        self.height=height
        self.x=x
        self.y=y
        self.bg_color=bg_color
        self.fg_color=fg_color
        #this should allow people to pass in 'left' 'Left' 'l' etc
        self.align=align.lower()[0]

    #start the panel, get the binary running in the background
    def start(self):
        command = ['dzen2',
                   '-w',str(self.width),
                   '-h',str(self.height),
                   '-x',str(self.x),
                   '-y',str(self.y),
                   '-fn',self.font,
                   '-ta',self.align,
                   '-bg',self.bg_color,
                   '-fg',self.fg_color
                   ]
        self.process=subprocess.Popen(command,stdin=subprocess.PIPE)

    #stop the panel, stop the binary from running in the background
    #note that communicate passes eof for us, and will block until
    #the process terminates
    def stop(self):
        self.process.communicate()

    #make sure the binary is running
    def is_running(self):
        if None!=self.process.poll():
            raise Exception("Can't print, dzen2 is not running")

    #print the text in the panel
    def print_text(self,text):
        self.is_running()
        self.process.stdin.write(text)
    def set_foreground(self,color=''):
        self.is_running()
        self.process.stdin.write('^fg('+color+')')
    def set_background(self,color=''):
        self.is_running()
        self.process.stdin.write('^bg('+color+')')

    #flush anything in the stdin buffer, and write a newline so
    #the panel will display it
    def flush(self):
        self.is_running()
        self.process.stdin.write('\n')
        self.process.stdin.flush()

def print_tags(dz,tags):
    bg_color = { '.':ink_black,
                  ':':ink_black,
                  '+':ink_purple,
                  '#':ink_purple,
                  '-':ink_black,
                  '%':ink_black,
                  '!':ink_black
                }
    fg_color = { '.':ink_white,
                  ':':ink_purple,
                  '+':ink_black,
                  '#':ink_black,
                  '-':ink_blue,
                  '%':ink_blue,
                  '!':ink_red
                }
    for i in tags:
        dz.set_foreground(fg_color[i[0]])
        dz.set_background(bg_color[i[0]])
        dz.print_text(i[1:])

def herbst_event_loop():
    #to get the info about the wm we want
    hc = herbstluft.HerbstluftClient()

    #get all our dimensions squared away
    screen_rect=hc.monitor_rect()
    panel_height=16
    panel_width=screen_rect[2]
    hc.pad(monitor=0,pad_up=panel_height)
    tags=hc.tag_status()

    #start up the 'message pump'
    hc_process = subprocess.Popen(['herbstclient','--idle'],stdout=subprocess.PIPE)
    hc_event=''
    #start up the timer, inside this block, a timer_event hook will be
    #emitted every n seconds
    with herbstluft.HerbstluftTimer(seconds=10) as hc_timer:
        #start the panel
        dz2=Dzen2(panel_width,panel_height,bg_color=ink_black,fg_color=ink_white)
        dz2.start()
        while 'reload' != hc_event:
            hc_event=hc_process.stdout.readline().strip()
            if 'tag'==hc_event[:3]:
                tags=hc.tag_status()
            print_tags(dz2,tags)
            dz2.flush()
        dz2.stop()
    hc_process.terminate()
    hc_process.communicate()

def spawn_panel(monitor=0):
    pid=os.fork()
    #if pid is 0 then we are in the child process
    if 0==pid:
       herbst_event_loop()
