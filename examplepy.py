from gi.repository import GObject, Gtk, Gdk, GtkSource, Gedit

class ExamplePyViewActivatable(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "ExamplePyViewActivatable"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        print "Plugin created for", self.view
#        print self.view.get_editable()
#        print self.view.get_insert_spaces_instead_of_tabs()
#        print dir(self.view)
        self._handlers = [
            self.view.connect('key-release-event', self.on_key_press_event)
        ]
        print self.view.get_tab_width()
        print self.view.get_indent_width()

        print self.view.set_tab_width(8)
        print self.view.set_indent_width(4)

        print self.view.get_tab_width()
        print self.view.get_indent_width()



    def do_deactivate(self):
        print "Plugin stopped for", self.view
        for handler in self._handlers:
            if handler is not None:
                self.view.disconnect(handler)



    def do_update_state(self):
        # Called whenever the view has been updated
        print "Plugin update for", self.view



    def on_key_press_event(self, view, event):
        print 'Key released'

        # Only take care of backspace and shift+backspace
        mods = Gtk.accelerator_get_default_mod_mask()

        # if tab or shift+tab:
        # with shift+tab key is GDK_ISO_Left_Tab (yay! on win32 and mac too!)

        if ((event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_KP_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab) and ((event.state & mods) == 0 or (event.state & mods) == Gdk.ModifierType.SHIFT_MASK)):
            print "TAB PRESETOOO"
        else:
            print "TAB NICHT PRESSED"


        return False
