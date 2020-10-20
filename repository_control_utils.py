import hashlib
import os
import zlib
import json
import shutil
from IPython import embed

REPO_ENTRY = 'repos'
OBJECTS_ENTRY = 'objects'
INDEX_ENTRY = 'index'

INDEX_CURR = 'curr'
INDEX_ROOT = 'root'
INDEX_ADOPTS = 'adopts'


def init_repo(path, data):
    if not os.path.exists(path):
        raise Exception('Invalid path given')

    if repo_exists(path):
        raise Exception('Repo already exists')

    os.makedirs(repo_objects_path(path))
    write_repo_object(path, data)
    write_repo_index(path, build_index_dict(data))


def copy_repo(old_path, new_path):
    if not old_path or not new_path:
        raise Exception('Invalid paths given')

    if old_path != new_path:
        remove_repo(new_path)
        shutil.copytree(repo_path(old_path), repo_path(new_path))


def remove_repo(path):
    if repo_exists(path):
        shutil.rmtree(repo_path(path))


def repo_exists(path):
    return os.path.exists(repo_path(path))


def repo_path(path):
    file_path_hash = get_hash(path)
    return os.path.join(REPO_ENTRY, file_path_hash[0:2], file_path_hash[2:])


def repo_index_path(path):
    return os.path.join(repo_path(path), INDEX_ENTRY)


def repo_objects_path(path):
    return os.path.join(repo_path(path), OBJECTS_ENTRY)


def repo_index(path):
    with open(repo_index_path(path), 'rb') as f:
        binary_index = f.read()
        index = zlib.decompress(binary_index)
        index = json.loads(index)
    return index


def write_repo_index(path, dict_data):
    with open(repo_index_path(path), 'wb') as f:
        data = json.dumps(dict_data)
        binary_data = zlib.compress(data.encode())
        f.write(binary_data)


def repo_index_curr(path):
    index = repo_index(path)
    return index[INDEX_CURR]


def update_repo_index_curr(path, file_hash):
    index = repo_index(path)
    index[INDEX_CURR] = file_hash
    write_repo_index(path, index)


def build_index_dict(data):
    file_hash = get_hash(data)
    index = {
        INDEX_ROOT: file_hash,
        INDEX_CURR: file_hash,
        INDEX_ADOPTS: [],
        file_hash: []
    }
    return index


def repo_object(path, file_hash):
    with open(repo_object_path(path, file_hash), 'rb') as f:
        binary_data = f.read()
        encoded_data = zlib.decompress(binary_data)
        data = encoded_data.decode()
    return data


def repo_object_path(path, file_hash):
    return os.path.join(repo_objects_path(path), file_hash)


def repo_object_exists(path, file_hash):
    return os.path.exists(repo_object_path(path, file_hash))


def write_repo_object(path, data):
    file_hash = get_hash(data)
    with open(os.path.join(repo_objects_path(path), file_hash), 'wb') as f:
        data = zlib.compress(data.encode())
        f.write(data)


def append_repo_object(path, data, parent, adopted=False):
    index = repo_index(path)
    file_hash = get_hash(data)
    index[parent].append(file_hash)
    index[INDEX_CURR] = file_hash

    if file_hash not in index:
        index[file_hash] = []

    if adopted:
        index[INDEX_ADOPTS].append((parent, file_hash))

    write_repo_index(path, index)
    write_repo_object(path, data)


def get_hash(data):
    return hashlib.sha1(data.encode()).hexdigest()


def build_bridge(path, data):
    parent = repo_index_curr(path)
    append_repo_object(path, data, parent, adopted=True)
