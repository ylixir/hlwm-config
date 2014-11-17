# vim: set fileencoding=utf8 :
import os
import re
import subprocess
import time
import locale
import herbstluft
import dzen2

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


def get_date():
    return time.strftime('%a %d %b %Y %R %Z')
def get_volume():
    percent=re.compile(b'[0-9]+%')
    mute=re.compile(b'\[o[nf]')
    result=subprocess.check_output(['amixer','get','Master'])
    vol=int(percent.search(result).group()[:-1])
    #is it muted?
    ismute=False
    if b'f'==mute.search(result).group()[-1:]:
        ismute=True
    return (vol,ismute)
def get_brightness():
    try:
        with open('/sys/class/backlight/intel_backlight/brightness','r') as f:
            brightness=int(f.read())*100
        with open('/sys/class/backlight/intel_backlight/max_brightness','r') as f:
            brightness//=int(f.read())
    except:
        brightness=0
    return int(brightness)
#returns (power_now,energy_now,energy_full_design,status)
def get_battery():
    try:
        with open('/sys/class/power_supply/BAT0/energy_now','r') as f:
            energy_now=int(f.read())
        with open('/sys/class/power_supply/BAT0/power_now','r') as f:
            power_now=int(f.read())
        with open('/sys/class/power_supply/BAT0/energy_full_design','r') as f:
            energy_full_design=int(f.read())
        with open('/sys/class/power_supply/BAT0/status','r') as f:
            status=f.read().strip()
    except:
        energy_now=1
        power_now=1
        energy_full_design=1
        status='Discharging'
    return (power_now,energy_now,energy_full_design,status)

def print_separator(dz):
    dz.set_foreground_color(ink_blue)
    dz.put_text(' | ')
    dz.set_foreground_color()

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
        utf_i=i.decode('utf-8')
        dz.set_foreground_color(fg_color[utf_i[:1]])
        dz.set_background_color(bg_color[utf_i[:1]])
        dz.put_text(utf_i[1:])

    dz.set_background_color()
    dz.set_foreground_color()

def print_window_title(dz,title):
    dz.put_text(title)

#battery is (power_now,energy_now,energy_full_design,status)
def print_battery_status(dz,battery):
    dz.put_text('{:.2f}W '.format(float(battery[0])/1000000))
    dz.put_text(str(battery[1]*100//battery[2])+'% ')
    #Discharging
    if 'D'==battery[3][0]:
        time=str(battery[1]*60//battery[0]%60)
        while len(time)<2:
            time='0'+time
        time=str(battery[1]//battery[0])+':'+time
    #Charging
    elif 'C'==battery[3][0]:
        time=str((battery[2]-battery[1])*60//battery[0]%60)
        while len(time)<2:
            time='0'+time
        time=str((battery[2]-battery[1])//battery[0])+':'+time
    #Full
    else:
        time=battery[3]
    dz.put_text(time)

def print_screen_brightness(dz,brightness):
    if 10>brightness:
        dz.set_foreground_color(ink_green)
    elif 25>brightness:
        dz.set_foreground_color(ink_purple)
    elif 50>brightness:
        dz.set_foreground_color(ink_orange)
    else:
        dz.set_foreground_color(ink_red)
    dz.put_text(str(brightness))
    dz.put_text('☼')
    dz.set_foreground_color()

def print_sound_volume(dz,volume):
    if 0==volume[0] or True==volume[1]:
        dz.set_foreground_color(ink_red)
    elif 30>volume[0]:
        dz.set_foreground_color(ink_orange)
    elif 60>volume[0]:
        dz.set_foreground_color(ink_purple)
    else:
        dz.set_foreground_color(ink_green)
    dz.put_text(str(volume[0]))
    dz.put_text('♪')
    dz.set_foreground_color()

def print_date(dz,date):
    dz.put_text(date)

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
        dz2=dzen2.Dzen2(panel_width,panel_height,bg_color=ink_black,fg_color=ink_white)
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
                #subprocess.call(['xbacklight',command])
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
            dz2.set_text_alignment('left')
            print_tags(dz2,tags)

            dz2.set_text_alignment('center')
            print_window_title(dz2,window_title)

            dz2.set_text_alignment('right')

            print_battery_status(dz2,battery)
            print_separator(dz2)
            print_screen_brightness(dz2,brightness)
            print_separator(dz2)
            print_sound_volume(dz2,volume)
            print_separator(dz2)
            print_date(dz2,date)

            dz2.flush()

            hc_event=(hc_process.stdout.readline()).decode('utf-8').strip()

        dz2.stop()
    hc_process.terminate()
    hc_process.communicate()

def spawn_panel(monitor=0):
    pid=os.fork()
    #if pid is 0 then we are in the child process
    if 0==pid:
       herbst_event_loop()
