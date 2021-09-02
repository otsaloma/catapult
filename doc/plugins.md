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
import catapult


class HelloPlugin(catapult.Plugin):

    title = "Hello"

    def launch(self, window, id):
        self.debug(f"Copying {id!r} to the clipboard")
        catapult.util.copy_text_to_clipboard(id)

    def search(self, query):
        query = query.strip().lower()
        if query in "hello":
            self.debug(f"Found hello for {query!r}")
            yield catapult.SearchResult(
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

* Define your preferences as subclasses of `catapult.PreferencesItem`
  and list those under your plugin's class attribute
  `preferences_items`.

* Define a class attribute under your plugin's class called
  `conf_defaults` and list the configuration options there. Based on
  that a `PluginConfigurationStore` object will be made available under
  your plugin class as `conf` and likewise for each preferences item
  instance. Plugin configuration files are written automatically to
  `~/.config/catapult/plugins/<name>.conf`.

See the plugins shipped with Catapult for examples of the above.

## Guidelines

In your plugin, you get access to the `catapult` module and everything
under it. This does not mean that you should access anything or
everything from there as some parts will not have a stable API and will
change without notice. There is no strict definition of a plugin-exposed
API, but as a rough guideline, below is a list of what you can probably
safely use.

```python
catapult.Plugin
catapult.PreferencesItem
catapult.SearchResult
catapult.util
```

## API Status

Catapult is pre-1.0 software and the plugin API is liable to change in a
backwards-incompatible manner with new releases, although efforts will
be made to avoid that if reasonably possible.

## References

* https://github.com/otsaloma/catapult/blob/master/catapult/plugin.py
* https://github.com/otsaloma/catapult/tree/master/catapult/plugins
* https://lazka.github.io/pgi-docs/
