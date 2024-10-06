2024-10-06: Catapult 1.1
========================

* Add setting to show non-native apps i.e. ignore the `OnlyShowIn`
  attribute of desktop files (#29)
* Fix the light theme and `@import` rules in general (#28)

2024-04-03: Catapult 1.0.1
==========================

* Don't make build depend on flake8

2024-04-03: Catapult 1.0
========================

* Remember choices also for prefixes of search query, e.g. if searching
  for "music", also save choice for "musi", "mus", "mu" and "m" (this
  should help avoid results jumping back and forth in certain cases)
* Limit results returned per plugin (default 24) to avoid issues with
  huge file indexes paired with short query strings (#23)
* Use `xdg-screensaver lock` in the session plugin to lock the screen in
  GNOME (instead of the earlier `gnome-screensaver-command --lock`)
* Update installation to use just a Makefile and a private package
  under $PREFIX/share/catapult

2023-08-31: Catapult 0.999
==========================

* Fix result list scrolling
* Fix deleting clipboard items (#20)

2023-08-09: Catapult 0.99
=========================

* Fix copying to the clipboard

2023-07-23: Catapult 0.9
========================

* Use GTK 4 (#15)
* Drop Keybinder, users need to do the keybinding themselves
* Window positioning on screen no longer works, users can configure
  their own window manager to center all new windows
* See the updated README regarding the above regressions
* Show window initially by default, remove `--show`, add `--hide` (if
  you have Catapult configured to start when you login to your desktop,
  you probably want to add `--hide` there)
* Add dependency on the gapplication binary (part of GLib, but might
  be packaged separately, e.g. libglib2.0-bin on Debian)

2023-01-05: Catapult 0.6
========================

* Add search icon next to input
* Refresh default themes
* Allow overriding parts of the theme with `~/.config/catapult/user.css` (#14)

2022-10-23: Catapult 0.5.1
==========================

* Allow deleting clipboard history items using the delete key

2022-10-03: Catapult 0.5
========================

* Add a clipboard history plugin (default trigger "cc", requires a
  clipboard manager source, currently supports gpaste)
* Update apps plugin index every time the launcher window is shown,
  making new installed apps show up instantly in search results (#13)
* Specify limited API for plugins under `catapult.api`
* When installing, don't relay `PREFIX` to `setup.py` as many distros
  interpret that differently. Use `SETUP_PREFIX` separately if needed,
  e.g. for building a distro package, you could use something like `make
  DESTDIR=pkg PREFIX=/usr SETUP_PREFIX=/usr install`. See `Makefile` for
  details.
* Raise Python dependency to 3.8 or greater

2022-06-08: Catapult 0.4.1
==========================

* Create directory for logging

2022-06-06: Catapult 0.4
========================

* Update exchange rates once a week for the calculator plugin
* Don't crash the whole app if a plugin throws an error
* Write log to `~/.local/share/catapult/catapult.log`

2022-04-02: Catapult 0.3.2
==========================

* Fix caret color
* Add Dutch translation (Heimen Stoffels)

2021-09-30: Catapult 0.3.1
==========================

* Fix plugin configuration sometimes not being saved

2021-09-05: Catapult 0.3
========================

* Plugins can now have configuration files (#4)
* Add make build target (scabala, #2)

2021-07-20: Catapult 0.2
========================

* Redesigned preferences dialog
* Plugins can now define preferences
* Better icon

2021-06-06: Catapult 0.1.4
==========================

* Update window position if primary monitor changed

2021-03-24: Catapult 0.1.3
==========================

* Handle errors writing configuration files
* Write configuration files atomically
* Avoid the main window popping up when editing toggle key

2021-03-18: Catapult 0.1.2
==========================

* Fix result list initial scroll position

2021-03-17: Catapult 0.1.1
==========================

* Fix about and preferences dialog modality and positioning

2021-03-16: Catapult 0.1
========================

* Initial release
