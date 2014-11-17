#!/usr/bin/env python
# vim: set fileencoding=utf8 :

import herbstluft
import subprocess

with herbstluft.HerbstluftChain() as hc:
    #we want alt as our mod. mod4 would give us the super(windows) key
    mod=herbstluft.mod1
    shift=herbstluft.shift
    enter=herbstluft.enter
    control=herbstluft.control
    tab=herbstluft.tab

    #let the daemons know that the autostart file is being reloaded
    hc.emit_hook('reload')

    #lock it to speed things up
    hc.lock()

    #reset keybindings then set them up
    hc.keyunbind('all')
    hc.keybind(mod+shift+'q','close')
    hc.keybind(mod+shift+'r','reload')
    hc.keybind(mod+shift+'e','quit')
    hc.keybind(mod+enter,'spawn xterm')
    hc.keybind(mod+'d','spawn dmenu_run')

    #hc.keybind('XF86AudioRaiseVolume','spawn amixer -q set Master 5%+')
    #hc.keybind('XF86AudioLowerVolume','spawn amixer -q set Master 5%-')
    #hc.keybind('XF86AudioMute','spawn amixer -q set Master toggle')
    hc.keybind('XF86AudioRaiseVolume','spawn herbstclient emit_hook volume_raise')
    hc.keybind('XF86AudioLowerVolume','spawn herbstclient emit_hook volume_lower')
    hc.keybind('XF86AudioMute','spawn herbstclient emit_hook volume_mute')
    #hc.keybind('XF86MonBrightnessUp','spawn xbacklight +5')
    #hc.keybind('XF86MonBrightnessDown','spawn xbacklight -5')
    hc.keybind('XF86MonBrightnessUp','spawn herbstclient emit_hook brightness_up')
    hc.keybind('XF86MonBrightnessDown','spawn herbstclient emit_hook brightness_down')

    hc.keybind(mod+'h','focus left')
    hc.keybind(mod+'l','focus right')
    hc.keybind(mod+'j','focus down')
    hc.keybind(mod+'k','focus up')

    hc.keybind(mod+shift+'h','shift left')
    hc.keybind(mod+shift+'l','shift right')
    hc.keybind(mod+shift+'j','shift down')
    hc.keybind(mod+shift+'k','shift up')

    hc.keybind(mod+control+'space','split explode')
    hc.keybind(mod+'u','split bottom 0.5')
    hc.keybind(mod+'o','split right 0.5')

    resizestep=0.05
    hc.keybind(mod+control+'h','resize left +'+str(resizestep))
    hc.keybind(mod+control+'l','resize right +'+str(resizestep))
    hc.keybind(mod+control+'j','resize down +'+str(resizestep))
    hc.keybind(mod+control+'k','resize up +'+str(resizestep))

    hc.keybind(mod+'r','remove')
    hc.keybind(mod+'space','cycle_layout')
    hc.keybind(mod+'s','floating toggle')
    hc.keybind(mod+'f','fullscreen toggle')
    hc.keybind(mod+'p','pseudotile toggle')

    hc.keybind(mod+tab,'cycle_all +1')
    hc.keybind(mod+shift+tab,'cycle_all -1')
    hc.keybind(mod+'c','cycle')
    hc.keybind(mod+'i','jumpto urgent')

    #skipping the tag stuff starting at line 86 of the autostart.sh
    for i in range(1,10):
        hc.add(str(i))
        hc.keybind(mod+str(i),'use_index '+str(i-1))
        hc.keybind(mod+shift+str(i),'move_index '+str(i-1))
    #ditch the 'default' tag
    #unfortunately, this will have the side effect of switching to
    #the tag at the second index position, needs to be fixed
    hc.use_index(1)
    hc.merge_tag('default','1')

    #skipping the mouse stuff from line 98 in autostart.sh
    #i don't really get how the mouse works tbh, so just leave it out
    hc.mouseunbind('all')

    #reset floating and tiling themes
    hc.attr(path='theme.tiling.reset',new_value='1')
    hc.attr(path='theme.floating.reset',new_value='1')

    #okay now the theme
    hc.set('frame_bg_transparent',1)
    hc.set('frame_transparent_width',1)
    hc.attr(path='theme.background_color',new_value='#1e1e27')

    hc.set('frame_border_normal_color','#1e1e27')
    hc.set('frame_bg_normal_color','#cfbfad')
    hc.attr(path='theme.normal.color',new_value='#cfbfad')
    hc.attr(path='theme.inner_color',new_value='#1e1e27')
    hc.attr(path='theme.outer_color',new_value='#1e1e27')
    hc.set('always_show_frame',1)

    hc.attr(path='theme.floating.outer_color',new_value='#1e1e27')

    #hc.attr(path='theme.active.color',new_value='#c080d0')
    hc.set('frame_border_active_color','#1e1e27')
    hc.set('frame_bg_active_color','#808bed')
    hc.attr(path='theme.active.color',new_value='#808bed')
   
    hc.attr(path='theme.urgent.color',new_value='#f0ad6d')

    hc.set('frame_border_width',1)
    hc.set('frame_gap',4)
    hc.attr(path='theme.border_width',new_value=3)
    hc.attr(path='theme.inner_width',new_value=1)
    hc.attr(path='theme.outer_width',new_value=1)

    hc.attr(path='theme.floating.border_width',new_value=4)
    hc.attr(path='theme.floating.inner_width',new_value=1)
    hc.attr(path='theme.floating.outer_width',new_value=1)

    hc.set('window_gap',0)
    hc.set('frame_padding',0)
    hc.set('smart_window_surroundings',0)
    hc.set('smart_frame_surroundings',1)
    hc.set('mouse_recenter_gap',0)
    hc.set('focus_follows_mouse',1)

    #rule stuff
    hc.unrule('all')
    hc.rule('focus=on') #focus new clients
    hc.rule("windowtype~'_NET_WM_WINDOW_TYPE_(DIALOG|UTILITY|SPLASH)' pseudotile=on")
    hc.rule("windowtype='_NET_WM_WINDOW_TYPE_DIALOG' focus=on")
    hc.rule("windowtype~'_NET_WM_WINDOW_TYPE_(NOTIFICATION|DOCK|DESKTOP)' manage=off")

    #all done, unlock and let her rip
    hc.unlock()

    #set tree_style '╾│ ├└╼─┐'
    hc.set('tree_style','╾│ ├└╼─┐')

import panel
panel.spawn_panel()

subprocess.call(['xli','-onroot','Wallpapers/linux_arch_linux_gnulinux_1920_1366x768_miscellaneoushi.com.jpg'])
subprocess.call(['xset','-dpms','s','off'])
subprocess.call(['xrdb','.Xresources'])
subprocess.call(['xhost','+local:'])
