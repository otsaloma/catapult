Catapult Launcher
=================

[![Plugins](https://img.shields.io/badge/community-plugins-blueviolet)](https://github.com/topics/catapult-plugin)
[![Themes](https://img.shields.io/badge/community-themes-blueviolet)](https://github.com/topics/catapult-theme)

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

| Dependency       | Version |
| :--------------- | :------ |
| Python           | ≥ 3.8   |
| PyGObject        |         |
| GLib             |         |
| GTK              | ≥ 4.0   |
| Cairo            |         |
| Pango            |         |
| libqalculate     |         |
| Noto Sans        |         |
| Noto Color Emoji |         |

The Noto fonts are needed by the characters plugin which uses the fonts
to render icons of characters and emojis on the fly.

On Debian/Ubuntu you can install these with the following command.

    sudo apt install fonts-noto-core \
                     fonts-noto-color-emoji \
                     gettext \
                     gir1.2-glib-2.0 \
                     gir1.2-gtk-4.0 \
                     gir1.2-pango-1.0 \
                     libglib2.0-bin \
                     python3 \
                     python3-cairo \
                     python3-dev \
                     python3-gi \
                     qalc

Then, to install Catapult, run commands

    make PREFIX=/usr/local build
    sudo make PREFIX=/usr/local install

## Documentation

### Keybinding to Activate Catapult

Catapult cannot do a global activation keybinding for you, instead you
need to do it yourself in your desktop/distro settings. Catapult is a
single-instance app, so executing `catapult` will start a new instance
if not yet running or else activate the existing instance. So, that is
the command you can bind to your key of choice.

* [GNOME](https://help.gnome.org/users/gnome-help/stable/keyboard-shortcuts-set.html.en)

### Window Position on Screen

Catapult cannot position its own window on your screen, which means that
it will be positioned wherever your window manager defaults to or
considers appropriate. You can configure your window manager to center
all new windows by default, which should center the Catapult window too
(at least horizontally, vertically the window height changes along with
the search results).

* GNOME: `gsettings set org.gnome.mutter center-new-windows true`

### Starting Automatically

If you did a keybinding as above running command `catapult`, you
shouldn't need to pre-start Catapult in the background, it will simply
start the first time you need it. If, however, you find the initial
startup slow (maybe indexing a lot of files), you can use tools provided
by your desktop/distro to set Catapult to start automatically already
when you log in to your desktop. To start in the background, use command
`catapult --hide`.

* [GNOME](https://help.gnome.org/users/gnome-help/stable/shell-apps-auto-start.html.en)
* [Ubuntu](https://help.ubuntu.com/stable/ubuntu-help/startup-applications.html.en)

### Customizing the Theme

You can override parts of the theme by editing
`~/.config/catapult/user.css`, a file which is created the first time
you start Catapult. You can edit the file while Catapult is running and
use `:reload-theme` in Catapult to apply the changes.

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

### Developers

* [Writing Plugins](https://github.com/otsaloma/catapult/blob/master/doc/plugins.md)
* [Writing Themes](https://github.com/otsaloma/catapult/blob/master/doc/themes.md)
