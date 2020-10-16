import argparse
import collections
import configparser
import hashlib
import os
import re
import sys
import zlib
import json

argparser = argparse.ArgumentParser(description="The stupid content tracker")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")

argsp = argsubparsers.add_parser("root", help="Read the latest object.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to find the repository.")

argsp = argsubparsers.add_parser("append", help="Append the latest object.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to find the repository.")


def repo_init(path):
    with open(path, 'r') as f:
        data = f.read()
    dir_name = hashlib.sha1(path.encode()).hexdigest()
    file_name = hashlib.sha1(data.encode()).hexdigest()
    binary_data = zlib.compress(data.encode())
    repo_dirs = './repos/{}/{}/{}/'.format(dir_name[0:2], dir_name[2:], 'objects')

    if not os.path.exists(repo_dirs):
        os.makedirs(repo_dirs)
        with open(os.path.join(repo_dirs, file_name), 'wb') as f:
            f.write(binary_data)

        index = {
            'root': file_name,
            'current': file_name,
            file_name: []
        }
        index = json.dumps(index)
        binary_index = zlib.compress(index.encode())
        repo_index = './repos/{}/{}/{}'.format(dir_name[0:2], dir_name[2:], 'index')
        with open(repo_index, 'wb') as f:
            f.write(binary_index)
    else:
        raise Exception('Repo already exists!')


def repo_exists(path):
    dir_name = hashlib.sha1(path.encode()).hexdigest()
    repo_path = './repos/{}/{}'.format(dir_name[0:2], dir_name[2:])
    return os.path.exists(repo_path)


def repo_path(path):
    if repo_exists(path):
        dir_name = hashlib.sha1(path.encode()).hexdigest()
        return './repos/{}/{}'.format(dir_name[0:2], dir_name[2:])
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


def read_repo_object(path, file_hash):
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


def append_object(path, file_hash, data, parent):
    index = repo_index(path)
    if parent != file_hash:
        index[parent].append(file_hash)
        index['current'] = file_hash
        if file_hash not in index:
            index[file_hash] = []
        write_repo_index(path, index)
        write_repo_object(path, file_hash, data)
        return True
    return False


def update_index_curr(path, file_hash):
    index = repo_index(path)
    index['current'] = file_hash
    write_repo_index(path, index)


def get_current_file_hash(path):
    index = repo_index(path)
    return index['current']


def get_hash(data):
    return hashlib.sha1(data.encode()).hexdigest()
