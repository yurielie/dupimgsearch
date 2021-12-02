# dupimgsearch
`dupimgsearch` is a CLI tool to detects duplicate images in given directories.

It generates a database of image hashes (average hash) in a local file and reduces the time to search for duplicate images next time.

## Install

```bash
pip install git+https://github.com/yurielie/dupimgsearch
```

## Usage (Execute Directory)

### Search duplicate images

`find` searches duplicate images in given directories as `dir ...` and registers them in local database file.

```bash
dupimgsearch find [--output OUTPUT] [--recursive] [--extension EXTENSION [EXTENSION ...]] \
                            [--strict] [--autoremove] [--yes] [--nodatabase] [--verbose] [dirs ...]
```

`dir ...` allows each directories to have alias by joining with `&`, like as `"./images&my-pictures"`.

If `dir ...` is empty, `find` searches duplicate images in all directories you registered.

if `dir ...` contains only new directories you have never given, `find` searches duplicate images in directories as `dir ...` and registered directories.

If `dir ...` contains registered directories, `find` searches duplicate images in only given directories as `dir ...`.


### Remove duplicate images

`dupimgsearch remove` command to remove duplicate images listed up in given files.

```bash
dupimgsearch remove [--file FILE [FILE ...]] [--yes] [--verbose]
```

### Purge directories

`dupimgsearch purge` command to purge directories registered in database file.

```bash
dupimgsearch purge database [database ...]
```

`database` are absolute pathes or aliases.

## Depenencies

+ `numpy`
+ `cv2`
+ `argparse`
+ `tqdm`

## Uninstall

```
pip uninstall dupimgsearch
```

# License

MIT License
