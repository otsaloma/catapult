# -*- coding: utf-8-unix -*-

# Installation directories without DESTDIR.
# Only used by install, build uses no variables at all.
PREFIX    = /usr/local
BINDIR    = $(PREFIX)/bin
DATADIR   = $(PREFIX)/share
LIBDIR    = $(DATADIR)/catapult
LOCALEDIR = $(DATADIR)/locale

# EDITOR must wait!
EDITOR = nano

# Packagers tend to just run 'make'.
.DEFAULT_GOAL = build

build:
	@echo "BUILDING PYTHON PACKAGE..."
	rm -rf build
	mkdir -p build
	cp -R catapult build
	find build -type d -name __pycache__ -prune -exec rm -rf {} +
	find build -type d -name test -prune -exec rm -rf {} +
	# Source data for emoji-list.txt, not needed at runtime.
	find build/catapult/plugins/unicode -type f ! -name "*.txt" -delete
	@echo "BUILDING TRANSLATIONS..."
	rm -f po/LINGUAS
	ls po/*.po | cut -d/ -f2 | cut -d. -f1 > po/LINGUAS
	mkdir -p build/mo
	for LOCALE in `cat po/LINGUAS`; do msgfmt po/$$LOCALE.po -o build/mo/$$LOCALE.mo; done
	@echo "BUILDING DESKTOP FILE..."
	msgfmt --desktop -d po \
	--template data/io.otsaloma.catapult.desktop.in \
	-o build/io.otsaloma.catapult.desktop
	@echo "BUILDING APPDATA FILE..."
	msgfmt --xml -d po \
	--template data/io.otsaloma.catapult.appdata.xml.in \
	-o build/io.otsaloma.catapult.appdata.xml
	touch build/.complete

check:
	flake8 catapult
	flake8 bin/catapult-start
	flake8 bin/catapult-start.in
	flake8 conftest.py

clean:
	rm -rf build
	rm -rf dist
	rm -f po/LINGUAS
	rm -f po/*~
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +

install:
	test -f build/.complete
	@echo "INSTALLING PYTHON PACKAGE..."
	rm -rf $(DESTDIR)$(LIBDIR)/catapult
	mkdir -p $(DESTDIR)$(LIBDIR)
	cp -R build/catapult $(DESTDIR)$(LIBDIR)
	sed \
	-e "s|^DATA_DIR = .*$$|DATA_DIR = Path('$(LIBDIR)')|" \
	-e "s|^LOCALE_DIR = .*$$|LOCALE_DIR = Path('$(LOCALEDIR)')|" \
	build/catapult/__init__.py > $(DESTDIR)$(LIBDIR)/catapult/__init__.py
	grep -qF "$(LIBDIR)" $(DESTDIR)$(LIBDIR)/catapult/__init__.py
	grep -qF "$(LOCALEDIR)" $(DESTDIR)$(LIBDIR)/catapult/__init__.py
	@echo "INSTALLING LAUNCHERS..."
	mkdir -p $(DESTDIR)$(BINDIR)
	cp -f bin/catapult $(DESTDIR)$(BINDIR)
	sed "s|%LIBDIR%|$(LIBDIR)|" bin/catapult-start.in > $(DESTDIR)$(BINDIR)/catapult-start
	grep -qF "$(LIBDIR)" $(DESTDIR)$(BINDIR)/catapult-start
	chmod +x $(DESTDIR)$(BINDIR)/catapult-start
	@echo "INSTALLING DATA FILES..."
	mkdir -p $(DESTDIR)$(LIBDIR)/themes
	cp -f data/catapult.css $(DESTDIR)$(LIBDIR)
	cp -f data/themes/*.css $(DESTDIR)$(LIBDIR)/themes
	@echo "INSTALLING GNOME SHELL EXTENSIONS..."
	mkdir -p $(DESTDIR)$(DATADIR)/gnome-shell/extensions/catapult-clipboard@otsaloma.io
	cp -f data/gnome-shell/catapult-clipboard@otsaloma.io/* $(DESTDIR)$(DATADIR)/gnome-shell/extensions/catapult-clipboard@otsaloma.io
	mkdir -p $(DESTDIR)$(DATADIR)/gnome-shell/extensions/catapult-windows@otsaloma.io
	cp -f data/gnome-shell/catapult-windows@otsaloma.io/* $(DESTDIR)$(DATADIR)/gnome-shell/extensions/catapult-windows@otsaloma.io
	@echo "INSTALLING ICONS..."
	mkdir -p $(DESTDIR)$(DATADIR)/icons/hicolor/scalable/apps
	mkdir -p $(DESTDIR)$(DATADIR)/icons/hicolor/symbolic/apps
	cp -f data/io.otsaloma.catapult.svg $(DESTDIR)$(DATADIR)/icons/hicolor/scalable/apps
	cp -f data/io.otsaloma.catapult-symbolic.svg $(DESTDIR)$(DATADIR)/icons/hicolor/symbolic/apps
	@echo "INSTALLING TRANSLATIONS..."
	for MO in build/mo/*.mo; do \
	LOCALE=`basename $$MO .mo`; \
	mkdir -p $(DESTDIR)$(LOCALEDIR)/$$LOCALE/LC_MESSAGES; \
	cp -f $$MO $(DESTDIR)$(LOCALEDIR)/$$LOCALE/LC_MESSAGES/catapult.mo; \
	done
	@echo "INSTALLING DESKTOP FILE..."
	mkdir -p $(DESTDIR)$(DATADIR)/applications
	cp -f build/io.otsaloma.catapult.desktop $(DESTDIR)$(DATADIR)/applications
	@echo "INSTALLING APPDATA FILE..."
	mkdir -p $(DESTDIR)$(DATADIR)/metainfo
	cp -f build/io.otsaloma.catapult.appdata.xml $(DESTDIR)$(DATADIR)/metainfo
	test -z "$(DESTDIR)" && update-desktop-database "$(DATADIR)/applications" || true

# Interactive!
release:
	$(MAKE) check test clean
	@echo "BUMP VERSION NUMBER"
	$(EDITOR) catapult/__init__.py
	@echo "ADD RELEASE NOTES"
	$(EDITOR) NEWS.md
	$(EDITOR) data/io.otsaloma.catapult.appdata.xml.in
	appstreamcli validate --no-net data/io.otsaloma.catapult.appdata.xml.in
	killall catapult || true
	sudo $(MAKE) build install clean
	/usr/local/bin/catapult --debug
	tools/release
	@echo "REMEMBER TO UPDATE WEBSITE"

test:
	pytest -xs catapult

# Interactive!
translations:
	tools/update-translations

.PHONY: build check clean install release test translations
