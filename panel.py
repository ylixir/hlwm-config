# coding=utf8
import os
import re
import subprocess
import time
import locale
import herbstluft

ink_blue='#808bed'
ink_black='#1e1e27'
ink_purple='#c080d0'
ink_bright_purple='#ff8bff'
#ink_red='#6d3030'
ink_red='#af4f4b'
ink_white='#cfbfad'
ink_orange='#cd8b00'
ink_bright_green='#00ff8b'
ink_green='#409090'

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
    aligned_width = {'l':0,'r':50,'c':0}
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
        #figure out the width of the text
        #textwidth doesn't seem to do well with accents and whatnot
        #so we try to handle that
        working=text
        working=working.decode('utf-8')
        working=strip_unicode(working)
        working=working.encode('utf-8')
        self.aligned_width[self.alignment]+=int(subprocess.check_output([self.textwidth_path,self.font,working]))
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

        #write out the centered text
        self.process.stdin.write('^p(_CENTER)')
        self.process.stdin.write('^p(-'+str(self.aligned_width['c']/2)+')')
        self.process.stdin.write(self.aligned_text['c'])
        #write out the right aligned text
        self.process.stdin.write('^p(_RIGHT)')
        self.process.stdin.write('^p(-'+str(self.aligned_width['r'])+')')
        self.process.stdin.write(self.aligned_text['r'])

        #write out the newline and flush the buffer to display everything
        self.process.stdin.write('\n')
        self.process.stdin.flush()
        #don't forget to reset our string buffers
        self.aligned_text = {'l':'','r':'','c':''}
        self.aligned_width = {'l':0,'r':50,'c':0}

def get_date():
    return time.strftime('%a %d %b %Y %R %Z')
def get_volume():
    percent=re.compile('[0-9]+%')
    mute=re.compile('\[o[nf]')
    result=subprocess.check_output(['amixer','get','Master'])
    vol=int(percent.search(result).group()[:-1])
    #is it muted?
    ismute=False
    if 'f'==mute.search(result).group()[-1:]:
        ismute=True
    return (vol,ismute)
def get_brightness():
    try:
        with file('/sys/class/backlight/acpi_video0/brightness') as f:
            brightness=f.read()
    except:
        brightness=0
    return int(brightness)
#returns (power_now,energy_now,energy_full_design,status)
def get_battery():
    try:
        with file('/sys/class/power_supply/BAT0/energy_now') as f:
            energy_now=int(f.read())
        with file('/sys/class/power_supply/BAT0/power_now') as f:
            power_now=int(f.read())
        with file('/sys/class/power_supply/BAT0/energy_full_design') as f:
            energy_full_design=int(f.read())
        with file('/sys/class/power_supply/BAT0/status') as f:
            status=f.read().strip()
    except:
        energy_now=1
        power_now=1
        energy_full_design=1
        status='Discharging'
    return (power_now,energy_now,energy_full_design,status)

def print_tags(dz,tags):
    bg_color = { '.':ink_black,
                  ':':ink_black,
                  '+':ink_bright_purple,
                  '#':ink_bright_purple,
                  '-':ink_black,
                  '%':ink_black,
                  '!':ink_black
                }
    fg_color = { '.':ink_white,
                  ':':ink_bright_purple,
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
def print_window_title(dz,title):
    pass
#battery is (power_now,energy_now,energy_full_design,status)
def print_battery_status(dz,battery):
    pass
def print_screen_brightness(dz,brightness):
    pass
def print_sound_volume(dz,volume):
    pass
def print_date(dz,date):
    pass

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
        window_title=''
        battery=get_battery()
        brightness=get_brightness()
        volume=get_volume()
        while 'reload' != hc_event:
            if 'tag'==hc_event[:3]:
                tags=hc.tag_status()
            elif 'timer_event'==hc_event:
                date=get_date()
                battery=get_battery()
            elif 'volume'==hc_event[:6]:
                if 'raise'==hc_event[7:]:
                    command='5%+'
                elif 'lower'==hc_event[7:]:
                    command='5%-'
                elif 'mute'==hc_event[7:]:
                    command='toggle'
                subprocess.call(['amixer','-q','set','Master',command])
                volume=get_volume()
            elif 'brightness'==hc_event[:10]:
                if 'up'==hc_event[11:]:
                    command='+5'
                elif 'down'==hc_event[11:]:
                    command='-5'
                subprocess.call(['xbacklight',command])
                brightness=get_brightness()
            elif 'focus_changed'==hc_event[:13] or 'window_title_changed'==hc_event[:20]:
                splitted=hc_event.split('\t')
                if 3<=len(splitted):
                    window_title=splitted[2]
                else:
                    window_title=''
            elif 'quit_panel'==hc_event:
                break
            elif 'togglehidepanel'==hc_event:
                #TODO
                pass
            dz2.set_alignment('center')
            dz2.print_text(window_title)
            dz2.set_alignment('left')
            print_tags(dz2,tags)
            dz2.set_alignment('right')
            dz2.set_background()
            #returns (power_now,energy_now,energy_full_design,status)
            #battery=get_battery()
            dz2.print_text('{:.2f}W '.format(float(battery[0])/1000000))
            dz2.print_text(str(battery[1]*100/battery[2])+'% ')
            #Discharging
            if 'D'==battery[3][0]:
                time=str(battery[1]*60/battery[0]%60)
                while len(time)<2:
                    time='0'+time
                time=str(battery[1]/battery[0])+':'+time
            #Charging
            elif 'C'==battery[3][0]:
                time=str((battery[2]-battery[1])*60/battery[0]%60)
                while len(time)<2:
                    time='0'+time
                time=str((battery[2]-battery[1])/battery[0])+':'+time
            #Full
            else:
                time=battery[3]
            dz2.print_text(time)
            dz2.set_foreground(ink_blue)
            dz2.print_text(' | ')
            #brightness=get_brightness()
            if 10>brightness:
                dz2.set_foreground(ink_green)
            elif 25>brightness:
                dz2.set_foreground(ink_purple)
            elif 50>brightness:
                dz2.set_foreground(ink_orange)
            else:
                dz2.set_foreground(ink_red)
            dz2.print_text(str(get_brightness()))
            dz2.print_text('☼')
            dz2.set_foreground(ink_blue)
            dz2.print_text(' | ')
            #volume=get_volume()
            if 0==volume[0] or True==volume[1]:
                dz2.set_foreground(ink_red)
            elif 30>volume[0]:
                dz2.set_foreground(ink_orange)
            elif 60>volume[0]:
                dz2.set_foreground(ink_purple)
            else:
                dz2.set_foreground(ink_green)
            dz2.print_text(str(volume[0]))
            dz2.print_text('♪')
            dz2.set_foreground(ink_blue)
            dz2.print_text(' | ')
            dz2.set_foreground()
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
