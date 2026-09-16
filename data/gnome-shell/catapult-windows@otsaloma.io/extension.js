// -*- coding: utf-8-unix -*-

import Gio from "gi://Gio";
import Meta from "gi://Meta";
import Shell from "gi://Shell";

import * as Main from "resource:///org/gnome/shell/ui/main.js";
import {Extension} from "resource:///org/gnome/shell/extensions/extension.js";

const INTERFACE = `
<node>
  <interface name="org.gnome.Shell.Extensions.CatapultWindows">
    <method name="List">
      <arg type="a(tsss)" direction="out" name="windows"/>
    </method>
    <method name="Activate">
      <arg type="t" direction="in" name="id"/>
    </method>
  </interface>
</node>`;

export default class CatapultWindowsExtension extends Extension {

    enable() {
        this._dbus = Gio.DBusExportedObject.wrapJSObject(INTERFACE, this);
        this._dbus.export(Gio.DBus.session, "/org/gnome/Shell/Extensions/CatapultWindows");
    }

    disable() {
        this._dbus.unexport();
        this._dbus = null;
    }

    _listWindows() {
        // Same as the window switcher, most recently used first.
        // https://github.com/GNOME/gnome-shell/blob/main/js/ui/altTab.js
        return global.display.get_tab_list(Meta.TabList.NORMAL_ALL, null)
            .map(w => w.is_attached_dialog() ? w.get_transient_for() : w)
            .filter((w, i, a) => !w.skip_taskbar && a.indexOf(w) === i);
    }

    Activate(id) {
        const window = this._listWindows().find(w => w.get_id() === id);
        window && Main.activateWindow(window);
    }

    List() {
        const tracker = Shell.WindowTracker.get_default();
        return this._listWindows().map(window => {
            const app = tracker.get_window_app(window);
            return [
                window.get_id(),
                window.get_title() ?? "",
                app?.get_id() ?? "",
                app?.get_name() ?? "",
            ];
        });
    }

}
