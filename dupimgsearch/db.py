import os
import sys
import json
import collections
from typing import Tuple

from dupimgsearch import _utils

class HashDB(object):
    def __init__(self, db_path: str="", dirs: list[str]=[]):
        self._hash2path: dict[str, list[str]] = collections.defaultdict(list)
        self._path2hash: dict[str, str] = {}
        self.databases: dict[str, str] = {}
        self.db_aliases: dict[str, str] = {}
    
        if db_path != "":
            self.load_database(db_path, dirs)

    def get_pathes(self, hash: str) -> list[str]:
        if hash in self._hash2path.keys():
            return self._hash2path[hash]
        else:
            return []
    
    def get_hash(self, path: str) -> str:
        if path in self._path2hash:
            return self._path2hash[path]
        else:
            return ""
    
    def get_duplicate_hashes(self) -> list[str]:
        return [ hash for hash in self._hash2path.keys() if len(self._hash2path[hash]) > 1 ]

    def exists_hash(self, hash: str) -> bool:
        return hash in self._hash2path.keys()
    
    def exists_path(self, path: str) -> bool:
        return os.path.isfile(path) and path in self._path2hash.keys()
    
    def add(self, hash: str, path: str) -> None:
        self._hash2path[hash].append(path)
        self._path2hash[path] = hash
    
    def remove_path(self, path: str) -> None:
        if path in self._path2hash and self._path2hash[path] in self._hash2path.keys():
            hash: str = self._path2hash.pop(path)
            self._hash2path[hash].remove(path)

    def maybe_register_database(self, dirs: list[str]) -> list[str]:
        databases: list[str] = []
        for dir in dirs:
            db_dir, db_name = _utils.split_database_name(dir)
            if os.path.exists(db_name):
                print("error: don't use directory path as database name: '%s'" % db_name)
                sys.exit(1)
            
            if db_dir != "":
                self.databases[db_dir] = db_name
                if db_name != "":
                    self.db_aliases[db_name] = db_dir
                    databases.append(db_name)
                    _utils.logd("registered databases: %s as %s" % (db_dir, db_name))
                else:
                    databases.append(db_dir)
                    _utils.logd("registered databases: %s" % db_dir)
            else:
                _utils.logd("invalid database directory or name: '%s'" % dir)

        return databases

    def load_database(self, db_path: str, dirs: list[str]) -> None:
        dbs: list[str] = self.maybe_register_database(dirs)
        
        if not os.path.exists(db_path):
            _utils.logd("not found database: %s" % db_path)
            return
        
        _utils.logd("load from database: '%s'" % db_path)
        with open(db_path, mode='r') as f:
            j = json.load(f)

        if "databases" in j.keys():
            _utils.logd("registered database:")
            for path, alias in j["databases"].items():
                self.databases[path] = alias
                if alias != "":
                    self.db_aliases[alias] = path
                    _utils.logd("  %s & %s" % (path, alias))
                else:
                    _utils.logd("  %s" % path)
        
        db_to_load: list[str] = self.resolve_db_to_load(dbs)
        _utils.logd("database to load:\n\t%s" % str(db_to_load))

        data: dict[str, list[str]] = j["data"]
        for hash, paths in data.items():
            for path in paths:
                # TODO: failed to search when children directories of path is in db_to_load
                found: bool = False
                for db_dir in db_to_load:
                    if path.startswith(db_dir):
                        found = True
                        break
                if found and os.path.isfile(path):
                    self._hash2path[hash].append(path)
                    self._path2hash[path] = hash
            
        _utils.logd("loaded entries: %d" % len(self._path2hash))
        

    def update_database(self, db_path: str) -> None:
        for hash, paths in self._hash2path.items():
            if len(paths) == 0:
                del self._hash2path[hash]
        
        _utils.logd("update\n  databases: %d\n  data:\n    entries: %d\n    hashes: %d" % (len(self.databases), len(self._path2hash), len(self._hash2path)))
        with open(db_path, mode="w") as f:
            db: dict = {"databases": self.databases, "data": self._hash2path}
            f.write(json.dumps(db, indent=1, separators=(',',':')))

    def resolve_db_to_load(self, dbs: list[str]) -> list[str]:
        if len(dbs) == 0:
            _utils.logd("import from all databases")
            return [db for db in self.databases.keys()]
        
        include_existing_db: bool = False

        for db in dbs:
            if db in self.databases.keys() or db in self.db_aliases.keys():
                include_existing_db = True
                break

        if not include_existing_db:
            dbs += [path for path in self.databases.keys() if not path in dbs]
            _utils.logd("add all existing databases")

        return dbs
    
    def purge_database(self, database: list[str], db_path: str) -> int:
        purged_entries: int = 0
        dir: list[str] = []
        for db in database:
            if db in self.databases.keys():
                dir.append(db)
                del self.databases[db]
            if db in self.db_aliases.keys():
                dir.append(self.db_aliases[db])
                del self.databases[self.db_aliases[db]], self.db_aliases[db]
        
        purged_dir: Tuple[str, ...] = tuple(dir)
        for path in [p for p in self._path2hash.keys() if p.startswith(purged_dir)]:
            self._hash2path[self._path2hash[path]].remove(path)
            del self._path2hash[path]
            purged_entries += 1
        
        self.update_database(db_path)
    
        return purged_entries
