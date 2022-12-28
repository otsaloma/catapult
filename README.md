Catapult Launcher
=================

[![Gitter](https://badges.gitter.im/otsaloma/catapult.svg)](https://gitter.im/otsaloma/catapult)

Catapult is an app launcher for Linux. It allows you to easily launch
apps, open files and do basic calculations with a keyboard-driven user
interface. Custom plugins and themes can be loaded dynamically.

Catapult is Free Software released under the GNU General Public License
(GPL), see the file [`COPYING`](COPYING) for details. Small parts of the
code have been adapted from [Ulauncher][], likewise GPL. These are
indicated file-wise in the license headers of individual files.

[Ulauncher]: https://github.com/Ulauncher/Ulauncher

## Installing

### Packages

* [Arch Linux](https://aur.archlinux.org/packages/catapult)

### Source

Catapult requires the following.

| Dependency   | Version |
| :----------- | :------ |
| Python       | ≥ 3.8   |
| PyGObject    |         |
| GLib         |         |
| GTK          | ≥ 3.18  |
| Keybinder    |         |
| Pango        |         |
| libqalculate |         |

On Debian/Ubuntu you can install these with the following command.

    sudo apt install gettext \
                     gir1.2-glib-2.0 \
                     gir1.2-gtk-3.0 \
                     gir1.2-keybinder-3.0 \
                     gir1.2-pango-1.0 \
                     python3 \
                     python3-dev \
                     python3-gi \
                     qalc

Then, to install Catapult, run commands

    make build
    sudo make PREFIX=/usr/local install

## Documentation

### Starting Automatically

Use tools provided by your desktop/distro to set Catapult to start
automatically when you log in to your desktop. You can also create the
autostart file manually, usually under `~/.config/autostart`.

* [GNOME](https://help.gnome.org/users/gnome-help/stable/shell-apps-auto-start.html.en)
* [Ubuntu](https://help.ubuntu.com/stable/ubuntu-help/startup-applications.html.en)

### Customizing the Theme

Since Catapult 0.6, you can override parts of the theme by editing
`~/.config/catapult/user.css`, a file which is created the first time
you start Catapult 0.6 or later. You can edit the file while Catapult is
running and use `:reload-theme` in Catapult to apply the changes.

For example, to use the GNOME default font (Cantarell) for everything,
you can use

```css
.catapult-input-entry {
  font-family: "Cantarell", sans-serif;
}

.catapult-search-result-title {
  font-family: "Cantarell", sans-serif;
}

.catapult-search-result-description {
  font-family: "Cantarell", sans-serif;
}
```

Or, to use Ubuntu orange as the selection color, try

```css
@define-color selected-bg-color #e95420;
```

### Known Issues on Wayland

* Catapult cannot do a global toggle keybinding (Control+Space by
  default) for you, instead you need to do it yourself in your
  desktop/distro settings. Catapult is a single-instance app, so simply
  executing `catapult` will show the existing instance and that is the
  command you can bind to your key of choice.

* Window positioning might not work, which means that the Catapult
  window will be positioned on your screen wherever your window manager
  defaults to or considers appropriate. You can configure your window
  manager to center all new windows by default, which should center the
  Catapult window (excluding the search results).

### Developers

* [Writing Plugins](https://github.com/otsaloma/catapult/blob/master/doc/plugins.md)
* [Writing Themes](https://github.com/otsaloma/catapult/blob/master/doc/themes.md)
