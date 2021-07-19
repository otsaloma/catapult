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

## References

* https://github.com/otsaloma/catapult/blob/master/catapult/plugin.py
* https://github.com/otsaloma/catapult/tree/master/catapult/plugins
* https://lazka.github.io/pgi-docs/
