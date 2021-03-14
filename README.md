Catapult Launcher
=================

[![Gitter](https://badges.gitter.im/otsaloma/catapult.svg)](https://gitter.im/otsaloma/catapult)

Catapult is an app launcher for Linux. It ships with basic plugins to
launch apps, open files/folders and a calculator. The user interface is
based on GTK, but heavily themed, so it should fit any desktop
environment. Custom plugins and themes can be loaded dynamically.

Catapult is currently developed and tested on X/GNOME. It should work on
other desktop environments running X as well, but is unlikely to work
as-is on Wayland. PRs are welcome.

Catapult is Free Software released under the GNU General Public License
(GPL), see the file [`COPYING`](COPYING) for details. Small parts of the
code have been adapted from [Ulauncher][], likewise GPL. These are
indicated file-wise in the license headers of individual files.

[Ulauncher]: https://github.com/Ulauncher/Ulauncher

## Installing

Catapult requires the following.

| Dependency   | Version |
| :----------- | :------ |
| Python       | ≥ 3.6   |
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

Then, to install Catapult, run command

    sudo make PREFIX=/usr/local install

## Documentation

* [Writing Plugins](https://github.com/otsaloma/catapult/blob/master/doc/plugins.md)
* [Writing Themes](https://github.com/otsaloma/catapult/blob/master/doc/themes.md)
