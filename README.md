# AutoEvernote
The project provides python applications to generate useful notes of Evernote.

# Dependency

The app depends on the package, [EvernoteWrapper](https://github.com/CountChu/EvernoteWrapper) and [CountPackage](https://github.com/CountChu/CountPackage).

# Usages

## open_link.py

The app generates a note of Evernote that contains links of your local files or directories.

Usage 1: Generate the note, A - OpenLink, by the default config, config.yaml.
```
	python open_link.py
```

Usage 2: Generate the note, "A - OpenLink", by the specific config.
```
	python open_link.py -c config-YOUR.yaml
```