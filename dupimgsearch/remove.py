import os
import sys
import json

from dupimgsearch import _utils

def remove_duplicate_images(file: list[str], yes: bool=False) -> int:
    
    dup_img_pairs: list[list[str]] = []
    for f in file:
        if not os.path.isfile(f):
            print("error: not found such file: '%s'" % f)
            continue
        filepath: str = os.path.abspath(f)
        with open(filepath, mode='r') as j:
            dups: list = json.load(j)
        
            if len(dups) > 0:
                for pair in dups:
                    pair = [img for img in pair if os.path.isfile(img)]
                    if len(pair) >= 2:
                        dup_img_pairs.append(pair)
    
    _utils.logd(dup_img_pairs)

    if len(dup_img_pairs) == 0:
        sys.exit(0)

    if not yes:
        res: str = input("Remove %d image pairs (Y/n)>" % len(dup_img_pairs))
        if res.lower() != "y":
            sys.exit(0)
    
    removed_count: int = 0
    for pair in dup_img_pairs:
        for img in pair[1:]:
            os.remove(img)
            _utils.logd("remove %s" % img)
            removed_count += 1
    print("Removed %d images" % removed_count)
    return removed_count
