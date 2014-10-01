from gi.repository import GObject, Gtk, Gdk, GtkSource, Gedit, Gio, GLib

UI_STR = """
<ui>
    <toolbar name="ToolBar">
        <separator />
        <toolitem name="ExamplePyPluginDrawSpaces" action="ExamplePyPluginDrawSpaces" />
    </toolbar>
</ui>
"""

class ExamplePyWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = 'ExamplePyWindowActivatable'

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        # Retrieve enabled plugins list from Gsettings
        settings = Gio.Settings("org.gnome.gedit.plugins")
        enabledPlugins = settings.get_value("active-plugins").get_strv()[0]

        # Create toggle button
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("ExamplePyPluginActions")
        action = Gtk.ToggleAction("ExamplePyPluginDrawSpaces", "XXX", "Toggle Draw Spaces plugin", Gtk.STOCK_OK)

        # If draw spaces plugin is enabled then we enable toggle button
        if "drawspaces" in enabledPlugins:
            action.set_active(True)
        action.connect("toggled", self.on_spaces_toggle)
        self._actions.add_action(action)

        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_STR)
        manager.ensure_update()

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()

    def do_update_state(self):
        pass

    def on_spaces_toggle(self, action, data=None):
        self.do_update_state()
        settings = Gio.Settings("org.gnome.gedit.plugins")

        enabledPlugins = settings.get_value("active-plugins").get_strv()[0]
        resultSettings = None
        if "drawspaces" in enabledPlugins:
            enabledPlugins.remove("drawspaces")
        else:
            enabledPlugins.append("drawspaces")

        resultSettings = GLib.Variant.new_strv(enabledPlugins)
        settings.set_value("active-plugins", resultSettings)



class ExamplePyViewActivatable(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "ExamplePyViewActivatable"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        doc = self.view.get_buffer()
        self._handlers = [
            self.view.connect('key-release-event', self.on_key_release_event),
            self.view.connect('key-press-event', self.on_key_press_event)
        ]

        # Found something similar in autoTab plugin, where it waits for doc
        # to be loaded and only the applies tab width and indent, becaus seems
        # like plugin loading order is undefined and other plugins re-set these
        # values, so we wait for a while, so our settings are final.
        self._bufhandlers = [
            doc.connect('loaded', self.on_loaded)
        ]


    def on_loaded(self, view, event):
        self.view.set_tab_width(8)
        self.view.set_indent_width(4)

    def do_deactivate(self):
        print "Plugin stopped for", self.view
        for handler in self._handlers:
            if handler is not None:
                self.view.disconnect(handler)
        for handler in self._bufhandlers:
            if handler is not None:
                self.view.get_buffer().disconnect(handler)



    def do_update_state(self):
        # Called whenever the view has been updated
        pass



    def reverseTab(self, doc, lineNbr):
        lineIterStart = doc.get_iter_at_line(lineNbr)

        thereWasTab = False
        while lineIterStart.get_char() == '\t':
            thereWasTab = True
            lineIterStart.forward_char()

        lineIterEnd = lineIterStart.copy()

        if lineIterStart.get_char() == ' ':
            for i in xrange(0, 4):
                lineIterEnd.forward_char()
                if lineIterEnd.get_char() != ' ':
                    break

            doc.delete(lineIterStart, lineIterEnd)

        elif thereWasTab:
            lineIterStart.backward_char()
            doc.delete(lineIterStart, lineIterEnd)
            doc.insert(lineIterStart, "    ")

    def on_key_press_event(self, view, event):
        mods = Gtk.accelerator_get_default_mod_mask()
        # if tab or shift+tab:
        # with shift+tab key is GDK_ISO_Left_Tab (yay! on win32 and mac too!)
        if ((event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_KP_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab) and ((event.state & mods) == 0 or (event.state & mods) == Gdk.ModifierType.SHIFT_MASK)):

            if ((event.state & mods) == Gdk.ModifierType.SHIFT_MASK):
                doc = view.get_buffer()

                if doc.get_has_selection():
                    start_iter, end_iter = doc.get_selection_bounds()
                    start_line_nb = start_iter.get_line()
                    end_line_nb = end_iter.get_line()

                    doc.begin_user_action()

                    for i in xrange(start_line_nb, end_line_nb + 1):
                        self.reverseTab(doc, i)
                    doc.end_user_action()


                else:
                    doc.begin_user_action()

                    cursorLineNr = doc.get_iter_at_mark(doc.get_insert()).get_line()
                    self.reverseTab(doc, cursorLineNr)

                    doc.end_user_action()

                return True


        return False

    def on_key_release_event(self, view, event):

        mods = Gtk.accelerator_get_default_mod_mask()
        # if tab or shift+tab:
        # with shift+tab key is GDK_ISO_Left_Tab (yay! on win32 and mac too!)
        if ((event.keyval == Gdk.KEY_Tab or event.keyval == Gdk.KEY_KP_Tab or event.keyval == Gdk.KEY_ISO_Left_Tab) and ((event.state & mods) == 0 or (event.state & mods) == Gdk.ModifierType.SHIFT_MASK)):
            doc = view.get_buffer()


            if doc.get_has_selection():
                start_iter, end_iter = doc.get_selection_bounds()
                start_line_nb = start_iter.get_line()
                end_line_nb = end_iter.get_line()

                doc.begin_user_action()

                for i in xrange(start_line_nb, end_line_nb + 1):
                    lineIterStart = doc.get_iter_at_line(i)
                    while lineIterStart.get_char() == '\t':
                        lineIterStart.forward_char()

                    lineIterEnd = lineIterStart.copy()

                    while True:
                        lineIterEnd.forward_chars(8)
                        if lineIterStart.get_text(lineIterEnd) == "        ":
                            doc.delete(lineIterStart, lineIterEnd)
                            doc.insert(lineIterStart, "\t")
                            lineIterEnd = lineIterStart.copy()
                        else:
                            break
                doc.end_user_action()

            else:
#                doc.begin_user_action()
                cursorLineNr = doc.get_iter_at_mark(doc.get_insert()).get_line()
                lineIterStart = doc.get_iter_at_line(cursorLineNr)

                while lineIterStart.get_char() == '\t':
                    lineIterStart.forward_char()

                lineIterEnd = lineIterStart.copy()

                while True:
                    lineIterEnd.forward_chars(8)
                    if lineIterStart.get_text(lineIterEnd) == "        ":
                        doc.delete(lineIterStart, lineIterEnd)
                        doc.insert(lineIterStart, "\t")
                        lineIterEnd = lineIterStart.copy()
                    else:
                        break
#                doc.end_user_action()
#            print dir(doc)

        return False
