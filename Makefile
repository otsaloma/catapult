# -*- coding: utf-8-unix -*-

DESTDIR   =
PREFIX    = /usr/local
BINDIR    = $(DESTDIR)$(PREFIX)/bin
DATADIR   = $(DESTDIR)$(PREFIX)/share
LOCALEDIR = $(DESTDIR)$(PREFIX)/share/locale

# Paths to patch in files,
# referring to installed, final paths.
BINDIR_FINAL    = $(PREFIX)/bin
DATADIR_FINAL   = $(PREFIX)/share
LOCALEDIR_FINAL = $(PREFIX)/share/locale

# EDITOR must wait!
EDITOR = nano

build:
	@echo "BUILDING PYTHON PACKAGE..."
	mkdir -p build/catapult
	cp catapult/*.py build/catapult
	sed -i "s|^DATA_DIR = .*$$|DATA_DIR = Path('$(DATADIR_FINAL)/catapult')|" build/catapult/__init__.py
	sed -i "s|^LOCALE_DIR = .*$$|LOCALE_DIR = Path('$(LOCALEDIR_FINAL)')|" build/catapult/__init__.py
	fgrep -q "$(DATADIR_FINAL)/catapult" build/catapult/__init__.py
	fgrep -q "$(LOCALEDIR_FINAL)" build/catapult/__init__.py
	mkdir -p build/catapult/plugins
	cp catapult/plugins/*.py build/catapult/plugins
	mkdir -p build/catapult/plugins/unicode
	cp catapult/plugins/unicode/*.txt build/catapult/plugins/unicode
	@echo "BUILDING SCRIPTS..."
	mkdir -p build/bin
	cp bin/catapult build/bin/catapult
	cp bin/catapult-start.in build/bin/catapult-start
	sed -i "s|%LIBDIR%|$(DATADIR_FINAL)/catapult|" build/bin/catapult-start
	fgrep -q "$(DATADIR_FINAL)/catapult" build/bin/catapult-start
	chmod +x build/bin/catapult-start
	@echo "BUILDING TRANSLATIONS..."
	mkdir -p build/mo
	for LANG in `cat po/LINGUAS`; do msgfmt po/$$LANG.po -o build/mo/$$LANG.mo; done
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
	flake8 bin/catapult-start.in

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
	mkdir -p $(DATADIR)/catapult/catapult
	cp -f build/catapult/*.py $(DATADIR)/catapult/catapult
	mkdir -p $(DATADIR)/catapult/catapult/plugins
	cp -f build/catapult/plugins/*.py $(DATADIR)/catapult/catapult/plugins
	mkdir -p $(DATADIR)/catapult/catapult/plugins/unicode
	cp -f build/catapult/plugins/unicode/*.txt $(DATADIR)/catapult/catapult/plugins/unicode
	@echo "INSTALLING SCRIPTS..."
	mkdir -p $(BINDIR)
	cp -f build/bin/catapult $(BINDIR)
	cp -f build/bin/catapult-start $(BINDIR)
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
	for LANG in `cat po/LINGUAS`; do mkdir -p $(LOCALEDIR)/$$LANG/LC_MESSAGES; done
	for LANG in `cat po/LINGUAS`; do cp -f build/mo/$$LANG.mo $(LOCALEDIR)/$$LANG/LC_MESSAGES/catapult.mo; done
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
	appstream-util validate-relax --nonet data/io.otsaloma.catapult.appdata.xml.in
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
