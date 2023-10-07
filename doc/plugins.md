Writing Plugins
===============

To write a custom plugin for Catapult, put the following Python code
into file `~/.local/share/catapult/plugins/hello.py`. Then in Catapult,
type `:preferences` to get to the preferences dialog and you should be
able to activate the plugin by flipping the "Hello plugin" switch at the
bottom of the dialog. When developing your plugin, use `:reload-plugins`
to apply your changes. Use `self.debug` calls and run Catapult with
`catapult --debug` to see what's happening.

```python
from catapult.api import copy_text_to_clipboard
from catapult.api import Plugin
from catapult.api import SearchResult

class HelloPlugin(Plugin):

    title = "Hello"

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        copy_text_to_clipboard(id)

    def search(self, query):
        query = query.strip().lower()
        if query in "hello":
            self.debug(f"Found hello for {query!r}")
            yield SearchResult(
                description="hello",
                fuzzy=False,
                icon="application-x-executable",
                id="hello",
                offset="hello".index(query),
                plugin=self,
                score=1,
                title="Hello",
            )
```

## Configuration/Preferences

If your plugin needs to be user-configurable, i.e. needs items in the
preferences dialog and a configuration file, then do the following.

* Define your preferences as subclasses of
  `catapult.api.PreferencesItem` and list those under your plugin's
  class attribute `preferences_items`.

* List your configuration options under your plugin's class attribute
  `conf_defaults`. Based on that a `PluginConfigurationStore` object
  will be made available under your plugin class as `conf` and likewise
  for each preferences item instance. Plugin configuration files are
  written automatically to `~/.config/catapult/plugins/{name}.conf`.

See the plugins shipped with Catapult for examples of the above.

## API

The API available for plugins is defined under `catapult.api`.

https://github.com/otsaloma/catapult/blob/master/catapult/api.py

Catapult is pre-1.0 software and the plugin API is liable to change in a
backwards-incompatible manner with new releases, although efforts will
be made to avoid that if reasonably possible.

## References

* https://github.com/otsaloma/catapult/blob/master/catapult/plugin.py
* https://github.com/otsaloma/catapult/tree/master/catapult/plugins
* https://lazka.github.io/pgi-docs/
