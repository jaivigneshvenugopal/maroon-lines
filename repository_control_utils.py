import hashlib
import os
import zlib
import json
import shutil
from IPython import embed

REPOS = 'repos'
KEY = 'key'
INDEX = 'index'
OBJECTS = 'objects'

INDEX_CURR = 'curr'
INDEX_ROOT = 'root'
INDEX_ADOPTS = 'adopts'


def init_repo(file_path, file_data):
    if not os.path.exists(file_path):
        raise Exception('Unable to initialise repo: Invalid path given')

    if repo_exists(file_path):
        raise Exception('Unable to initialise repo: Repo already exists')

    os.makedirs(repo_objects_path(file_path))
    write_repo_key(file_path)
    write_repo_object(file_path, file_data)
    write_repo_index(file_path, build_index_dict(file_data))


def copy_repo(old_file_path, new_file_path):
    if not old_file_path or not new_file_path:
        raise Exception('Unable to copy repo: Invalid path/s given')

    if old_file_path != new_file_path:
        remove_repo(new_file_path)
        shutil.copytree(repo_path(old_file_path), repo_path(new_file_path))
        write_repo_key(new_file_path)


def remove_repo(file_path):
    if repo_exists(file_path):
        shutil.rmtree(repo_path(file_path))


def rebuilt_repo(file_path, file_data):
    remove_repo(file_path)
    init_repo(file_path, file_data)


def repo_exists(file_path):
    return os.path.exists(repo_path(file_path))


def repo_path(file_path):
    file_path_hash = get_hash(file_path)
    return os.path.join(REPOS, file_path_hash[0:2], file_path_hash[2:])


def repo_key_path(file_path):
    return os.path.join(repo_path(file_path), KEY)


def repo_index_path(file_path):
    return os.path.join(repo_path(file_path), INDEX)


def repo_objects_path(file_path):
    return os.path.join(repo_path(file_path), OBJECTS)


def repo_key(file_path):
    with open(repo_key_path(file_path), 'r') as f:
        key = f.read()
    return key


def write_repo_key(file_path):
    with open(repo_key_path(file_path), 'w') as f:
        f.write(file_path)


def repo_index(file_path):
    with open(repo_index_path(file_path), 'rb') as f:
        binary_index = f.read()
        json_index = zlib.decompress(binary_index)
        dict_index = json.loads(json_index)
    return dict_index


def write_repo_index(file_path, dict_index):
    with open(repo_index_path(file_path), 'wb') as f:
        json_index = json.dumps(dict_index)
        binary_index = zlib.compress(json_index.encode())
        f.write(binary_index)


def repo_index_curr_object(file_path):
    index = repo_index(file_path)
    return index[INDEX_CURR]


def update_repo_index_curr_object(file_path, file_hash):
    index = repo_index(file_path)
    index[INDEX_CURR] = file_hash
    write_repo_index(file_path, index)


def build_index_dict(file_data):
    file_hash = get_hash(file_data)
    index = {
        INDEX_ROOT: file_hash,
        INDEX_CURR: file_hash,
        INDEX_ADOPTS: [],
        file_hash: []
    }
    return index


def build_bridge(file_path, file_data):
    parent_file_hash = repo_index_curr_object(file_path)
    append_repo_object(file_path, file_data, parent_file_hash, adopted=True)


def repo_object(file_path, file_hash):
    with open(repo_object_path(file_path, file_hash), 'rb') as f:
        binary_file_data = f.read()
        encoded_file_data = zlib.decompress(binary_file_data)
        file_data = encoded_file_data.decode()
    return file_data


def repo_object_path(file_path, file_hash):
    return os.path.join(repo_objects_path(file_path), file_hash)


def repo_object_exists(file_path, file_hash):
    return os.path.exists(repo_object_path(file_path, file_hash))


def write_repo_object(file_path, file_data):
    file_hash = get_hash(file_data)
    with open(repo_object_path(file_path, file_hash), 'wb') as f:
        binary_file_data = zlib.compress(file_data.encode())
        f.write(binary_file_data)


def append_repo_object(file_path, file_data, parent_file_hash, adopted=False):
    index = repo_index(file_path)
    file_hash = get_hash(file_data)
    index[parent_file_hash].append(file_hash)
    index[INDEX_CURR] = file_hash

    if file_hash not in index:
        index[file_hash] = []

    if adopted:
        index[INDEX_ADOPTS].append((parent_file_hash, file_hash))

    write_repo_index(file_path, index)
    write_repo_object(file_path, file_data)


def get_hash(file_data):
    return hashlib.sha1(file_data.encode()).hexdigest()
