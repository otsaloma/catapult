# -*- coding: utf-8-unix -*-

DESTDIR   =
PREFIX    = /usr/local
DATADIR   = $(DESTDIR)$(PREFIX)/share
LOCALEDIR = $(DESTDIR)$(PREFIX)/share/locale

# EDITOR must wait!
EDITOR = nano

check:
	flake8 .
	flake8 bin/*

clean:
	rm -rf build
	rm -rf catapult.egg-info
	rm -rf dist
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__

install:
	@echo "INSTALLING PYTHON PACKAGE..."
	./setup-partial.py install $(if $(DESTDIR),--root=$(DESTDIR),) --prefix=$(PREFIX)
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
	msgfmt po/$$LANG.po -o $(LOCALEDIR)/$$LANG/LC_MESSAGES/catapult.mo; \
	done
	@echo "INSTALLING DESKTOP FILE..."
	mkdir -p $(DATADIR)/applications
	msgfmt --desktop -d po \
	--template data/io.otsaloma.catapult.desktop.in \
	-o $(DATADIR)/applications/io.otsaloma.catapult.desktop
	@echo "INSTALLING APPDATA FILE..."
	mkdir -p $(DATADIR)/metainfo
	msgfmt --xml -d po \
	--template data/io.otsaloma.catapult.appdata.xml.in \
	-o $(DATADIR)/metainfo/io.otsaloma.catapult.appdata.xml

# Interactive!
release:
	$(MAKE) check test clean
	@echo "BUMP VERSION NUMBER"
	$(EDITOR) catapult/__init__.py
	@echo "ADD RELEASE NOTES"
	$(EDITOR) TODO.md
	$(EDITOR) NEWS.md
	$(EDITOR) data/io.otsaloma.catapult.appdata.xml.in
	killall catapult || true
	sudo $(MAKE) PREFIX=/usr/local install clean
	/usr/local/bin/catapult --debug
	tools/release
	@echo "REMEMBER TO UPDATE WEBSITE"

test:
	py.test -xs .

# Interactive!
translations:
	tools/update-translations

.PHONY: check clean install release test translations
