# -*- coding: utf-8-unix -*-

DESTDIR   =
PREFIX    = /usr/local
BINDIR    = $(DESTDIR)$(PREFIX)/bin
DATADIR   = $(DESTDIR)$(PREFIX)/share
LOCALEDIR = $(DESTDIR)$(PREFIX)/share/locale

# Allow overriding setup.py paths. Note that we can't set
# SETUP_PREFIX=PREFIX as many distros are automatically adding
# 'local', causing '/usr/local/local' and a broken install.
# https://bugzilla.redhat.com/show_bug.cgi?id=2026979
SETUP_ROOT   = $(DESTDIR)
SETUP_PREFIX =

# EDITOR must wait!
EDITOR = nano

# TODO: Use either 'pip3 install' or 'python3 -m build' + 'python3 -m
# installer' once either supports a sensible installation both from
# source (--prefix=/usr/local, whether implicit or explicit) and
# building a distro package (--destdir=pkg --prefix=/usr). As of 9/2022
# it seems setup.py is deprecated, but there is no replacement.

build:
	@echo "BUILDING PYTHON PACKAGE..."
	CATAPULT_PREFIX=$(PREFIX) ./setup-partial.py build
	@echo "BUILDING TRANSLATIONS..."
	mkdir -p build/mo
	for LANG in `cat po/LINGUAS`; do \
	echo $$LANG; \
	msgfmt po/$$LANG.po -o build/mo/$$LANG.mo; \
	done
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
	flake8 .
	flake8 bin/catapult-start

clean:
	rm -rf build
	rm -rf catapult.egg-info
	rm -rf dist
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__

install:
	test -f build/.complete
	@echo "INSTALLING PYTHON PACKAGE..."
	CATAPULT_PREFIX=$(PREFIX) ./setup-partial.py install \
	$(if $(SETUP_ROOT),--root=$(SETUP_ROOT),) \
	$(if $(SETUP_PREFIX),--prefix=$(SETUP_PREFIX),)
	@echo "INSTALLING SHELL SCRIPT..."
	mkdir -p $(BINDIR)
	cp -f bin/catapult $(BINDIR)
	chmod +x $(BINDIR)/catapult
	@echo "INSTALLING DATA FILES..."
	mkdir -p $(DATADIR)/catapult/themes
	cp -f data/catapult.css $(DATADIR)/catapult
	cp -f data/themes/*.css $(DATADIR)/catapult/themes
	@echo "INSTALLING ICONS..."
	mkdir -p $(DATADIR)/icons/hicolor/scalable/apps
	mkdir -p $(DATADIR)/icons/hicolor/symbolic/apps
	cp -f data/icons/io.otsaloma.catapult.svg $(DATADIR)/icons/hicolor/scalable/apps
	cp -f data/icons/io.otsaloma.catapult-symbolic.svg $(DATADIR)/icons/hicolor/symbolic/apps
	@echo "INSTALLING TRANSLATIONS..."
	for LANG in `cat po/LINGUAS`; do \
	echo $$LANG; \
	mkdir -p $(LOCALEDIR)/$$LANG/LC_MESSAGES; \
	cp -f build/mo/$$LANG.mo $(LOCALEDIR)/$$LANG/LC_MESSAGES/catapult.mo; \
	done
	@echo "INSTALLING DESKTOP FILE..."
	mkdir -p $(DATADIR)/applications
	cp -f build/io.otsaloma.catapult.desktop $(DATADIR)/applications
	@echo "INSTALLING APPDATA FILE..."
	mkdir -p $(DATADIR)/metainfo
	cp -f build/io.otsaloma.catapult.appdata.xml $(DATADIR)/metainfo

# Interactive!
release:
	$(MAKE) check test clean
	@echo "BUMP VERSION NUMBER"
	$(EDITOR) catapult/__init__.py
	@echo "ADD RELEASE NOTES"
	$(EDITOR) NEWS.md
	$(EDITOR) data/io.otsaloma.catapult.appdata.xml.in
	killall catapult || true
	sudo $(MAKE) PREFIX=/usr/local build install clean
	/usr/local/bin/catapult --debug
	tools/release
	@echo "REMEMBER TO UPDATE WEBSITE"

test:
	py.test -xs .

# Interactive!
translations:
	tools/update-translations

.PHONY: build check clean install release test translations
