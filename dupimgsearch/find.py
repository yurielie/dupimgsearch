import os
from typing import Tuple
import itertools
import glob

import numpy as np
import tqdm

from dupimgsearch import db, _utils

def find_duplicate_images(
    dir: list[str]=[],
    db_path: str="",
    recursive: bool=False,
    extension: list[str]=[".jpg", ".png"],
    strict: bool=False,
    nodatabase: bool=False,
    ) -> Tuple[list[list[str]], list[str]]:

    # extension must be Tuple
    if not strict:
        extension = [ e if e.startswith('.') else "." + e.lower() for e in extension] +  [ e if e.startswith('.') else "." + e.upper() for e in extension]
    exts = tuple(extension)
    _utils.logd("extensions: %s" % extension)

    # load hash databases
    hdb: db.HashDB = db.HashDB()
    if not nodatabase and db_path != "":
        hdb.load_database(db_path, dir)        

    # split dir if contain database name
    search_dirs: list[str] = []
    for d in dir:
        path, name = _utils.split_database_name(d)
        if path != "":
            search_dirs.append(path)
        elif name in hdb.db_aliases.keys():
            search_dirs.append(hdb.db_aliases[name])
    
    # search image files to generate hash
    new_images: list[str]  = [ img for dir in search_dirs for img in glob.glob("%s/**" % (os.path.abspath(dir)), recursive=recursive) if img.endswith(exts) and not hdb.exists_path(img)]
    _utils.logd("found new imamges: %d" % len(new_images))
    
    # hash images
    skipped_images: list[str] = []
    hashed_image_num: int = 0
    img_process_bar: tqdm.tqdm = tqdm.tqdm(new_images, leave=False)
    ahash: str = ""
    for image in img_process_bar:
        img_process_bar.set_description(os.path.basename(image))
        ahash = _utils.generate_hash(_utils.imread(image))
        if ahash != "":                  
            hdb.add(ahash, image)
            hashed_image_num += 1
        else:
            skipped_images.append(image)
    _utils.logd("generated hashes: %d" % hashed_image_num)
    _utils.logd("skipped images: %d" % len(skipped_images))
    
    # check deep equality between same hash images
    duplicate_hashes: list[str] = hdb.get_duplicate_hashes()
    _utils.logd("%d images may be duplicate" % len(duplicate_hashes))
    duplicate_images: list[list[str]] = []
    for hash in tqdm.tqdm(duplicate_hashes, leave=False):
        image_names: list[str] = hdb.get_pathes(hash)
        image_arrays: list[np.ndarray] = [_utils.imread(image_name) for image_name in image_names]

        dup_imgs: set[str] = set()
        for i, j in list(itertools.combinations(range(len(image_names)), 2)):
            if np.array_equal(image_arrays[i], image_arrays[j]):
                dup_imgs.add(image_names[i])
                dup_imgs.add(image_names[j])
        if len(dup_imgs) > 0:
            duplicate_images.append(list(dup_imgs))
        
    print("found %d pairs that may be duplicate." % len(duplicate_images))
    
    if db_path != "":
        hdb.update_database(db_path)
    
    return duplicate_images, skipped_images