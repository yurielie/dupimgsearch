import os
import sys
import json
import argparse
from dupimgsearch import find, purge, remove, _utils

_conf_path: str = os.path.join(os.path.dirname(__file__), "config.json")

def _find(args: argparse.Namespace) -> None:
    if args.verbose:
        _utils.set_loglevel("debug")
    
    if not os.path.isdir(args.output):
        print("error: invalid directory path: '%s'" % args.output)
        sys.exit(1)
    
    if args.db_path == "" and not args.nodatabase:
        if len(args.dir) > 0:
            # initialize db
            db_dir, _ = _utils.split_database_name(args.dir[0])
            args.db_path = os.path.join(db_dir, ".db.json")
            print("initialize configure file:\n\tconfigure file: %s\n\tdb_path: %s" % (_conf_path, args.db_path))
            with open(_conf_path, mode='w', encoding='utf-8') as f:
                conf: dict[str, str] = {"path": args.db_path}
                json.dump(conf, f, indent=1, separators=(',',':'))
        else:
            print("error: no databases exist")
            sys.exit(1)
    elif not os.path.isfile(args.db_path):
        print("error: invalid path of database: '%s'" % args.db_path)
        sys.exit(1)
    
    dup, skip = find.find_duplicate_images(dir=args.dir, db_path=args.db_path, recursive=args.recursive, extension=args.extension, strict=args.strict, nodatabase=args.nodatabase)
    
    dup_imgs_file: str = ""
    if len(dup) > 0:
        dup_imgs_file = os.path.join(args.output, "duplicate_imgs.json")
        print("output duplicate images file to %s" % (dup_imgs_file))
        with open(dup_imgs_file, mode='w') as f:
            json.dump(dup, f, indent=2)
    if len(skip) > 0:
        skipped_imgs_file: str = os.path.join(args.output, "skipped_imgs.json")
        print("output skipped images file to %s" % (skipped_imgs_file))
        with open(skipped_imgs_file, mode='w') as f:
            json.dump(skip, f, indent=2)
    
    if args.autoremove is True and dup_imgs_file != "":
        setattr(args, "file", [dup_imgs_file])
        _remove(args)

def _remove(args: argparse.Namespace):
    remove.remove_duplicate_images(file=args.file, yes=args.yes)

def _purge(args: argparse.Namespace):
    if args.db_path == "":
        print("error: no database are generated")
        sys.exit(1)
    
    purge.purge_database(args.database, db_path=args.db_path)

def main():
    db_path: str = ""
    if os.path.isfile(_conf_path):
        with open(_conf_path, mode='r') as f:
            j = json.load(f)
            if "path" in j.keys():
                db_path = j["path"]
            else:
                print("error: invalid configure file: '%s'" % _conf_path)
                exit(1)

    ap: argparse.ArgumentParser = argparse.ArgumentParser(description="search duplicate images from given path", prog="dupimgsearch")
    sap: argparse._SubParsersAction = ap.add_subparsers(help="action for images")

    ## subcommand 'find'
    ap_find: argparse.ArgumentParser = sap.add_parser("find", help="help find")
    ap_find.add_argument('dir', type=str, nargs='*', default=[], help="directories to search duplicate images (when name database by 'DIRECTORY&ALIAS' [optional])")
    ap_find.add_argument('--output', '-o', type=str, default=".", help="output path of dup_imgs.json and skipped_img.json (default: '.')")
    ap_find.add_argument('--recursive','-r', action='store_true', help="search directories recursively")
    ap_find.add_argument('--extension', '-e', type=str, nargs='+', default=['jpg', 'png'], help="extension of image files to search (default: '['jpg', 'png']')")
    ap_find.add_argument('--strict', action='store_true', help="strict for extension (only enable when --extension is selected)")
    ap_find.add_argument('--autoremove', action='store_true', help="autoremove after search images")
    ap_find.add_argument('--yes', '-y', action='store_true', help="Don't ask for confirmation of remove")
    ap_find.add_argument('--nodatabase', action='store_true', help="not import from db and not output to db")
    ap_find.add_argument('--verbose', '-v', action='store_true', help="verbose process")
    ap_find.set_defaults(func=_find)

    ## subcommand 'remove'
    ap_remove: argparse.ArgumentParser = sap.add_parser("remove", help="help remove")
    ap_remove.add_argument('--file', '-f', type=str, nargs='+', default=["./duplicate_imgs.json"], help="path to duplicate_imgs.json (default: './duplicate_imgs.json')")
    ap_remove.add_argument('--yes', '-y', action='store_true', help="Don't ask for confirmation of remove")
    ap_remove.add_argument('--verbose', '-v', action='store_true', help="verbose process")
    ap_remove.set_defaults(func=_remove)

    ## subcommand 'purge'
    ap_purge: argparse.ArgumentParser = sap.add_parser('purge', help="help purge")
    ap_purge.add_argument('database', type=str, nargs='+', help="purged database path or name")
    ap_purge.set_defaults(func=_purge)

    ## parse arguments and call subcommand
    args: argparse.Namespace = ap.parse_args()
    setattr(args, "db_path", db_path)
    args.func(args)

if __name__ == "__main__":
    main()
