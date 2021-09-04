Writing Themes
==============

To write a custom theme for Catapult, put the following CSS into file
`~/.local/share/catapult/themes/hello.css`. Then in Catapult, type
`:preferences` to get to the preferences dialog and you should be able
to select your new "hello" theme. When developing your theme, use
`:reload-theme` to apply your changes.

```css
@import "@dark@";

@define-color bg-color #ffff55;
@define-color fg-color #2e3436;
@define-color selected-bg-color #3584e4;
@define-color selected-fg-color #ffffff;

.catapult-body {
  border-radius: 0;
  box-shadow: none;
}
```

## API Status

Catapult is pre-1.0 software and the theming API is liable to change in
a backwards-incompatible manner with new releases, although efforts will
be made to avoid that if reasonably possible.

## References

* https://github.com/otsaloma/catapult/tree/master/data/themes
* https://developer.gnome.org/gtk3/stable/theming.html
