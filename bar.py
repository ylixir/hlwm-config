# vim: set fileencoding=utf8 :

#generic statusbar class
class Bar(object):
    #every function in this prototype/stub thing just calls this
    def unimplemented(self):
        raise Exception('That functionality has not been implemented for this status bar.')

    #start up the status bar
    def start(self):
        self.unimplemented()
    #stop the status bar
    def stop(self):
        self.unimplemented()
    #find out if the status bar is currently running
    #returns True or False
    def is_running(self):
        self.unimplemented()

    #the core work routine. put some text on the bar
    def put_text(self,text):
        self.unimplemented()

    #set the colors, if color='' then reset to default color
    def set_foreground_color(self,color=''):
        self.unimplemented()
    def set_background_color(self,color=''):
        self.unimplemented()

    #set the alignment to left, right, or center
    def set_text_alignment(self,align):
        self.unimplemented()

    #do whatever housekeeping and flush everything out so it shows up
    def flush(self):
        self.unimplemented()
