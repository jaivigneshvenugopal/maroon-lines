import argparse
import collections
import configparser
import hashlib
import os
import re
import sys
import zlib
import json
import shutil


def repo_init(path):
    with open(path, 'r') as f:
        data = f.read()
    file_path_hash = hashlib.sha1(path.encode()).hexdigest()
    file_name = hashlib.sha1(data.encode()).hexdigest()
    repo_dirs = os.path.join('repos', file_path_hash[0:2], file_path_hash[2:], 'objects')

    if not os.path.exists(repo_dirs):
        os.makedirs(repo_dirs)
        with open(os.path.join(repo_dirs, file_name), 'wb') as f:
            binary_data = zlib.compress(data.encode())
            f.write(binary_data)

        index = {
            'root': file_name,
            'curr': file_name,
            'adopts': [],
            file_name: []
        }
        index = json.dumps(index)
        binary_index = zlib.compress(index.encode())
        repo_index = os.path.join('repos', file_path_hash[0:2], file_path_hash[2:], 'index')
        with open(repo_index, 'wb') as f:
            f.write(binary_index)
    else:
        raise Exception('Repo already exists!')


def copy_repo(old_path, new_path):
    if old_path != new_path:
        remove_repo(new_path)
        old_path_hash = hashlib.sha1(old_path.encode()).hexdigest()
        new_path_hash = hashlib.sha1(new_path.encode()).hexdigest()
        shutil.copytree(os.path.join('repos', old_path_hash[0:2], old_path_hash[2:]),
                        os.path.join('repos', new_path_hash[0:2], new_path_hash[2:]))


def remove_repo(path):
    if repo_exists(path):
        file_path_hash = hashlib.sha1(path.encode()).hexdigest()
        repo_path = os.path.join('repos', file_path_hash[0:2], file_path_hash[2:])
        shutil.rmtree(repo_path)


def repo_rebuilt(path):
    remove_repo(path)
    repo_init(path)


def repo_exists(path):
    file_path_hash = hashlib.sha1(path.encode()).hexdigest()
    repo_path = './repos/{}/{}'.format(file_path_hash[0:2], file_path_hash[2:])
    return os.path.exists(repo_path)


def repo_path(path):
    if repo_exists(path):
        file_path_hash = hashlib.sha1(path.encode()).hexdigest()
        return './repos/{}/{}'.format(file_path_hash[0:2], file_path_hash[2:])
    else:
        raise Exception('Repo does not exist!')


def repo_index(path):
    index_path = repo_index_path(path)
    with open(index_path, 'rb') as f:
        binary_index = f.read()
        index = zlib.decompress(binary_index)
        index = json.loads(index)
        return index


def repo_index_path(path):
    repo = repo_path(path)
    index_path = os.path.join(repo, 'index')
    return index_path


def repo_objects_path(path):
    repo = repo_path(path)
    repo_objects_dir = os.path.join(repo, 'objects')
    return repo_objects_dir


def read_repo_file(path, file_hash):
    text = None
    with open(os.path.join(repo_objects_path(path), file_hash), 'rb') as f:
        binary_data = f.read()
        encoded_data = zlib.decompress(binary_data)
        text = encoded_data.decode()
    return text


def write_repo_index(path, json_data):
    with open(repo_index_path(path), 'wb') as f:
        data = json.dumps(json_data)
        binary_data = zlib.compress(data.encode())
        f.write(binary_data)


def write_repo_object(path, file_hash, data):
    with open(os.path.join(repo_objects_path(path), file_hash), 'wb') as f:
        data = zlib.compress(data.encode())
        f.write(data)


def append_file_to_index(path, file_hash, data, parent, adopted=False):
    index = repo_index(path)
    index[parent].append(file_hash)
    index['curr'] = file_hash
    if file_hash not in index:
        index[file_hash] = []
    if adopted:
        index['adopts'].append((parent, file_hash))
    write_repo_index(path, index)
    write_repo_object(path, file_hash, data)


def update_index_curr(path, file_hash):
    index = repo_index(path)
    index['curr'] = file_hash
    write_repo_index(path, index)


def get_curr_file_hash(path):
    index = repo_index(path)
    return index['curr']


def get_hash(data):
    return hashlib.sha1(data.encode()).hexdigest()


def build_bridge(path, data):
    file_hash = get_hash(data)
    parent = get_curr_file_hash(path)
    append_file_to_index(path, file_hash, data, parent, adopted=True)


def file_hash_exists_in_repo(path, file_hash):
    file_path_hash = get_hash(path)
    return os.path.exists(os.path.join('repos', file_path_hash[0:2], file_path_hash[2:], 'objects', file_hash))



