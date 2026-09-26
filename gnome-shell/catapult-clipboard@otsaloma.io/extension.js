// -*- coding: utf-8-unix -*-

import Gio from "gi://Gio";
import GLib from "gi://GLib";
import Meta from "gi://Meta";

import {Extension} from "resource:///org/gnome/shell/extensions/extension.js";

Gio._promisify(Gio.InputStream.prototype, "read_bytes_async");
Gio._promisify(Meta.SelectionSource.prototype, "read_async");

const INTERFACE = `
<node>
  <interface name="org.gnome.Shell.Extensions.CatapultClipboard">
    <method name="List">
      <arg type="a(ts)" direction="out" name="items"/>
    </method>
    <method name="Delete">
      <arg type="t" direction="in" name="id"/>
      <arg type="b" direction="out" name="deleted"/>
    </method>
  </interface>
</node>`;

// History is kept in memory only, at module scope, as the module is loaded
// once per Shell process, but disable and enable are called also on screen
// lock and whenever an extension enabled before this one is disabled.
const history = [];
let nextId = 1;

export default class CatapultClipboardExtension extends Extension {

    enable() {
        this._cancellable = new Gio.Cancellable();
        this._selection = global.display.get_selection();
        this._ownerChangedId = this._selection.connect("owner-changed", (_selection, type, source) => {
            if (type === Meta.SelectionType.SELECTION_CLIPBOARD && source)
                this._record(source).catch(error => {
                    if (!error.matches?.(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))
                        console.debug(`Failed to read clipboard: ${error.message}`);
                });
        });
        this._dbus = Gio.DBusExportedObject.wrapJSObject(INTERFACE, this);
        this._dbus.export(Gio.DBus.session, "/org/gnome/Shell/Extensions/CatapultClipboard");
    }

    disable() {
        this._cancellable.cancel();
        this._cancellable = null;
        this._selection.disconnect(this._ownerChangedId);
        this._selection = null;
        this._dbus.unexport();
        this._dbus = null;
    }

    async _read(source, mimetype, maxSize) {
        const stream = await source.read_async(mimetype, this._cancellable);
        const chunks = [];
        let size = 0;
        try {
            while (true) {
                const bytes = await stream.read_bytes_async(65536, GLib.PRIORITY_DEFAULT, this._cancellable);
                if (bytes.get_size() === 0) break;
                size += bytes.get_size();
                if (size > maxSize) return null;
                chunks.push(bytes.toArray());
            }
        } finally {
            stream.close(null);
        }
        const data = new Uint8Array(size);
        let offset = 0;
        for (const chunk of chunks) {
            data.set(chunk, offset);
            offset += chunk.length;
        }
        return new TextDecoder().decode(data);
    }

    async _record(source) {
        const mimetypes = source.get_mimetypes();
        // Password managers such as KeePassXC mark secrets with this.
        if (mimetypes.includes("x-kde-passwordManagerHint")) return;
        // Files copied in a file manager, offered also as paths in text.
        if (mimetypes.includes("x-special/gnome-copied-files")) return;
        const mimetype = ["text/plain;charset=utf-8", "UTF8_STRING", "text/plain"]
            .find(x => mimetypes.includes(x));
        if (!mimetype) return;
        const text = await this._read(source, mimetype, 1048576);
        if (!text?.trim()) return;
        const i = history.findIndex(x => x.text === text);
        if (i >= 0) history.splice(i, 1);
        history.unshift({id: nextId++, text});
        history.splice(100);
    }

    Delete(id) {
        const i = history.findIndex(x => x.id === id);
        if (i >= 0) history.splice(i, 1);
        return i >= 0;
    }

    List() {
        return history.map(x => [x.id, x.text]);
    }
}
