# Hacker Theme for Zed

A dark, phosphor-green terminal theme for [Zed](https://zed.dev), inspired by
old CRT terminals: deep green-black backgrounds, glowing green keywords, amber
strings and numbers, and quiet comments that stay out of the way.

| Role | Color |
| --- | --- |
| Editor background | `#070e09` |
| Accent / keywords | `#3ef08c` |
| Functions | `#c4f26e` |
| Types | `#78e3cf` |
| Strings | `#ecd88a` |
| Numbers / constants | `#f5a65b` |
| Comments | `#5a8a66` |

## Install (local / dev extension)

1. Open Zed and run `zed: install dev extension` from the command palette.
2. Select this repository folder.
3. Open the theme selector (`cmd-k cmd-t`) and choose **Hacker Theme**.

Or set it in `settings.json`:

```json
{
  "theme": {
    "mode": "dark",
    "dark": "Hacker Theme",
    "light": "One Light"
  }
}
```

## Quick iteration without the extension

Copy the theme into Zed's user themes folder, and Zed reloads it when the file changes:

```sh
mkdir -p ~/.config/zed/themes
cp themes/hacker-theme.json ~/.config/zed/themes/
```

## License

MIT. See [LICENSE](LICENSE).
