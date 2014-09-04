# vim: set fileencoding=utf8 :
import bar
import subprocess
#from stack overflow, since textwidth seems to have trouble with
#unicode stuffs
import unicodedata
def strip_unicode(s):
    #strip accents
    normalized_s=unicodedata.normalize('NFD', str(s))
    text=''.join(c for c in normalized_s
                  if unicodedata.category(c) != 'Mn')
    #swap non latin stuff for M (a nice wide glyph hopefully)
    return ''.join([i if ord(i) < 128 else 'M' for i in text])

class Dzen2(bar.Bar):
    aligned_text = {'l':'','r':'','c':''}
    aligned_width = {'l':0,'r':50,'c':0}
    def __init__(self,width,height,x=0,y=0,font='-*-fixed-medium-*-*-*-12-*-*-*-*-*-*-*',bg_color='#000000',fg_color='#ffffff'):
        align='l'
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
    def put_text(self,text):
        #self.is_running()
        #self.process.stdin.write(text)
        self.aligned_text[self.alignment]+=str(text)
        #figure out the width of the text
        #textwidth doesn't seem to do well with accents and whatnot
        #so we try to handle that
        working=text
        #working=working.decode('utf-8')
        working=strip_unicode(working)
        working=working.encode('utf-8')
        self.aligned_width[self.alignment]+=int(subprocess.check_output([self.textwidth_path,self.font,working]))
    def set_foreground_color(self,color=''):
        #self.is_running()
        #self.process.stdin.write('^fg('+color+')')
        self.aligned_text[self.alignment]+='^fg('+color+')'
    def set_background_color(self,color=''):
        #self.is_running()
        #self.process.stdin.write('^bg('+color+')')
        self.aligned_text[self.alignment]+='^bg('+color+')'
    def set_text_alignment(self,align):
        self.alignment=align.lower()[0]

    #flush anything in the stdin buffer, and write a newline so
    #the panel will display it
    def flush(self):
        #make sure dzen is running
        self.is_running()
        #write out  the left aligned text
        self.process.stdin.write(b'^p(_LEFT)')
        self.process.stdin.write((self.aligned_text['l']).encode('utf-8'))

        #write out the centered text
        self.process.stdin.write(b'^p(_CENTER)')
        self.process.stdin.write(('^p(-'+str(self.aligned_width['c']/2)+')').encode('utf-8'))
        self.process.stdin.write(self.aligned_text['c'].encode('utf-8'))
        #write out the right aligned text
        self.process.stdin.write(b'^p(_RIGHT)')
        self.process.stdin.write(('^p(-'+str(self.aligned_width['r'])+')').encode('utf-8'))
        self.process.stdin.write(self.aligned_text['r'].encode('utf-8'))

        #write out the newline and flush the buffer to display everything
        self.process.stdin.write(b'\n')
        self.process.stdin.flush()
        #don't forget to reset our string buffers
        self.aligned_text = {'l':'','r':'','c':''}
        self.aligned_width = {'l':0,'r':50,'c':0}

