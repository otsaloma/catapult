// -*- coding: utf-8-unix -*-

import Gio from "gi://Gio";
import Meta from "gi://Meta";
import Shell from "gi://Shell";

import * as Main from "resource:///org/gnome/shell/ui/main.js";
import {Extension} from "resource:///org/gnome/shell/extensions/extension.js";
import {TransientSignalHolder} from "resource:///org/gnome/shell/misc/signalTracker.js";

const INTERFACE = `
<node>
  <interface name="org.gnome.Shell.Extensions.CatapultWindows">
    <method name="List">
      <arg type="a(tsss)" direction="out" name="windows"/>
    </method>
    <method name="Activate">
      <arg type="t" direction="in" name="id"/>
    </method>
    <method name="Preview">
      <arg type="t" direction="in" name="id"/>
    </method>
    <method name="ClearPreview"/>
  </interface>
</node>`;

export default class CatapultWindowsExtension extends Extension {

    enable() {
        this._preview = null;
        this._dbus = Gio.DBusExportedObject.wrapJSObject(INTERFACE, this);
        this._dbus.export(Gio.DBus.session, "/org/gnome/Shell/Extensions/CatapultWindows");
    }

    disable() {
        this.ClearPreview();
        this._dbus.unexport();
        this._dbus = null;
    }

    _finishPreview(accept = false) {
        const preview = this._preview;
        if (!preview)
            return;
        this._preview = null;
        preview.signals.destroy();
        const windows = new Set(global.display.list_all_windows());
        if (windows.has(preview.launcher) && !preview.launcherAbove)
            preview.launcher.unmake_above();
        if (accept)
            return;
        if (windows.has(preview.window) && preview.minimized && !preview.window.minimized) {
            Main.wm.skipNextEffect(preview.window.get_compositor_private());
            preview.window.minimize();
            // Raising flushes the pending hide, consuming the skipped animation.
            preview.window.raise();
        }
        for (const window of preview.stack) {
            if (windows.has(window) && window.located_on_workspace(preview.workspace))
                window.raise();
        }
        const focus = global.display.focus_window;
        if (focus && focus !== preview.launcher && windows.has(focus))
            focus.raise();
    }

    _listWindows() {
        // Same as the window switcher, most recently used first.
        // https://github.com/GNOME/gnome-shell/blob/main/js/ui/altTab.js
        const workspace = global.workspace_manager.get_active_workspace();
        return global.display.get_tab_list(Meta.TabList.NORMAL_ALL, workspace)
            .map(w => w.is_attached_dialog() ? w.get_transient_for() : w)
            // The tab list can also include attention-seeking windows on other workspaces.
            .filter((w, i, a) => w.located_on_workspace(workspace) &&
                !w.skip_taskbar && a.indexOf(w) === i);
    }

    Activate(id) {
        const window = this._listWindows().find(w => w.get_id() === id);
        this._finishPreview(window && this._preview?.window === window);
        window && Main.activateWindow(window);
    }

    ClearPreview() {
        this._finishPreview();
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

    Preview(id) {
        if (this._preview?.window.get_id() === id)
            return;
        this.ClearPreview();
        const launcher = global.display.focus_window;
        if (!launcher || Main.overview.visible || Main.sessionMode.isLocked)
            return;
        const app = Shell.WindowTracker.get_default().get_window_app(launcher);
        if (launcher.get_gtk_application_id() !== "io.otsaloma.catapult" &&
            app?.get_id() !== "io.otsaloma.catapult.desktop")
            return;
        const window = this._listWindows().find(w => w.get_id() === id);
        if (!window || window === launcher)
            return;
        const actor = window.get_compositor_private();
        const launcherActor = launcher.get_compositor_private();
        if (!actor || !launcherActor || actor.is_destroyed() || !launcherActor.visible)
            return;

        const workspace = global.workspace_manager.get_active_workspace();
        const signals = new TransientSignalHolder();
        this._preview = {
            window,
            launcher,
            workspace,
            signals,
            minimized: window.minimized,
            launcherAbove: launcher.is_above(),
            stack: global.display.sort_windows_by_stacking(workspace.list_windows()),
        };
        global.display.connectObject("notify::focus-window", () => {
            const focus = global.display.focus_window;
            this._finishPreview(focus === window || (focus && window.is_ancestor_of_transient(focus)));
        }, signals);
        window.connectObject(
            "unmanaged", () => this.ClearPreview(),
            "workspace-changed", () => this.ClearPreview(), signals);
        launcher.connectObject("unmanaged", () => this.ClearPreview(), signals);
        launcherActor.connectObject("notify::visible", () => {
            if (!launcherActor.visible)
                this.ClearPreview();
        }, signals);
        global.workspace_manager.connectObject("active-workspace-changed", () => this.ClearPreview(), signals);
        Main.overview.connectObject("showing", () => this.ClearPreview(), signals);
        Main.sessionMode.connectObject("updated", () => this.ClearPreview(), signals);

        if (!launcher.is_above())
            launcher.make_above();
        if (window.minimized) {
            Main.wm.skipNextEffect(actor);
            window.unminimize();
        }
        window.raise();
        launcher.raise();
    }

}
