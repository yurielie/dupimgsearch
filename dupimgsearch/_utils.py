import os
from typing import Literal, Optional, Tuple
import cv2
import numpy as np


class _UtilVar:
    log_level: Literal["debug", "none"] = "none"
    hash_func = cv2.img_hash.AverageHash_create()


def compress_hash(hash: np.ndarray) -> str:
    return ",".join(["%x" % n for n in hash[0]])

def generate_hash(img: Optional[np.ndarray]) -> str:
    if not img is None:
        return compress_hash(_UtilVar.hash_func.compute(img))
    else:
        print("skipped image: %s" % img)
        return ""

def imread(filename: str, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    n = np.fromfile(filename, dtype)
    img = cv2.imdecode(n, flags)
    if img is None:
        print("imread returns None by '%s'" % filename)
    return img

def split_database_name(database_name: str) -> Tuple[str, str]:
    path_name: list[str] = database_name.split("&", maxsplit=1)
    if len(path_name) == 2 and path_name[1] != "":
        return path_name[0], path_name[1]
    elif os.path.isdir(database_name):
        return os.path.abspath(database_name), ""
    else:
        return "", database_name

def set_loglevel(log_level: str):
    if log_level == "debug":
        _UtilVar.log_level = "debug"

def logd(*values: object):
    if _UtilVar.log_level == "debug":
        print(values)