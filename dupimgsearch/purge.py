from dupimgsearch import db

def purge_database(databases: list[str], db_path: str):
    hdb: db.HashDB = db.HashDB(db_path)
    purged_entries: int = hdb.purge_database(databases, db_path)
    print("purge %d databases, %d images" % (len(databases), purged_entries))