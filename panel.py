# coding=utf8
import os
import subprocess
import time
import locale
import herbstluft

ink_blue='#808bed'
ink_black='#1e1e27'
#ink_purple='#c080d0'
ink_purple='#ff8bff'
ink_red='#f0ad6d'
ink_white='#cfbfad'
ink_orange='#cd8b00'

#from stack overflow, since textwidth seems to have trouble with
#unicode stuffs
import unicodedata
def strip_unicode(s):
    #strip accents
    text=''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
    #swap non latin stuff for M (a nice wide glyph hopefully)
    return ''.join([i if ord(i) < 128 else 'M' for i in text])

class Dzen2(object):
    aligned_text = {'l':'','r':'','c':''}
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
        #self.current_text=self.aligned_text[align.lower()[0]]
        self.alignment=align.lower()[0]
        #check for the textwidth tool
        for tw in ['textwidth','dzen2-textwidth']:
            self.path=''
            try:
                subprocess.check_output(['which',tw])
                self.textwidth_path=tw
                break
            except subprocess.CalledProcessError:
                pass
        if ''==self.textwidth_path:
            raise Exception('This script requires the  textwidth tool of the dzen2 project')

    #start the panel, get the binary running in the background
    def start(self):
        command = ['dzen2',
                   '-w',str(self.width),
                   '-h',str(self.height),
                   '-x',str(self.x),
                   '-y',str(self.y),
                   '-fn',self.font,
                   #'-ta',self.align,
                   '-ta','l',
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
        #self.is_running()
        #self.process.stdin.write(text)
        self.aligned_text[self.alignment]+=text
    def set_foreground(self,color=''):
        #self.is_running()
        #self.process.stdin.write('^fg('+color+')')
        self.aligned_text[self.alignment]+='^fg('+color+')'
    def set_background(self,color=''):
        #self.is_running()
        #self.process.stdin.write('^bg('+color+')')
        self.aligned_text[self.alignment]+='^bg('+color+')'
    def set_alignment(self,align):
        self.alignment=align.lower()[0]

    #flush anything in the stdin buffer, and write a newline so
    #the panel will display it
    def flush(self):
        #make sure dzen is running
        self.is_running()
        #write out  the left aligned text
        self.process.stdin.write('^p(_LEFT)')
        self.process.stdin.write(self.aligned_text['l'])

        #figure out the width of the centered text
        #textwidth doesn't seem to do well with accents and whatnot
        #so we try to handle that
        working=self.aligned_text['c']
        working=working.decode('utf-8')
        working=strip_unicode(working)
        working=working.encode('utf-8')
        text_width=subprocess.check_output([self.textwidth_path,self.font,working])
        #write out the centered text
        self.process.stdin.write('^p(_CENTER)')
        self.process.stdin.write('^p(-'+str(int(text_width)/2)+')')
        self.process.stdin.write(self.aligned_text['c'])
        #figure out the width of the right aligned text
        #textwidth doesn't seem to do well with accents and whatnot
        #so we try to handle that
        working=self.aligned_text['r']
        working=working.decode('utf-8')
        working=strip_unicode(working)
        working=working.encode('utf-8')
        text_width=subprocess.check_output([self.textwidth_path,self.font,working])
        #write out the right aligned text
        self.process.stdin.write('^p(_RIGHT)')
        self.process.stdin.write('^p(-'+str(int(text_width))+')')
        self.process.stdin.write(self.aligned_text['r'])

        #write out the newline and flush the buffer to display everything
        self.process.stdin.write('\n')
        self.process.stdin.flush()
        #don't forget to reset our string buffers
        self.aligned_text = {'l':'','r':'','c':''}

def get_date():
        return time.strftime('%a %d %b %Y %R %Z')
def get_volume():
        return 10

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
    #shouldn't this just happen automatically? srsly
    locale.setlocale(locale.LC_ALL,'')
    #to get the info about the wm we want
    hc = herbstluft.HerbstluftClient()

    #get all our dimensions squared away
    screen_rect=hc.monitor_rect()
    panel_height=16
    panel_width=screen_rect[2]
    hc.pad(monitor=0,pad_up=panel_height)

    #start up the 'message pump'
    hc_process = subprocess.Popen(['herbstclient','--idle'],stdout=subprocess.PIPE)
    hc_event=''
    #start up the timer, inside this block, a timer_event hook will be
    #emitted every n seconds
    with herbstluft.HerbstluftTimer(seconds=10) as hc_timer:
        #start the panel
        dz2=Dzen2(panel_width,panel_height,bg_color=ink_black,fg_color=ink_white)
        dz2.start()
        #get the initial values for everything
        tags=hc.tag_status()
        date=get_date()
        while 'reload' != hc_event:
            if 'tag'==hc_event[:3]:
                tags=hc.tag_status()
            elif 'timer_event'==hc_event:
                date=get_date()
            dz2.set_alignment('left')
            print_tags(dz2,tags)
            dz2.set_alignment('right')
            dz2.print_text('♪')
            dz2.set_foreground()
            dz2.set_background()
            dz2.print_text(date)
            dz2.flush()

            hc_event=hc_process.stdout.readline().strip()

        dz2.stop()
    hc_process.terminate()
    hc_process.communicate()

def spawn_panel(monitor=0):
    pid=os.fork()
    #if pid is 0 then we are in the child process
    if 0==pid:
       herbst_event_loop()
