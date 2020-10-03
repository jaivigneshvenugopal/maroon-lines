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


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)

    if   args.command == "init"        : repo_init(args)
    elif args.command == "root"        : read_root_object(args)
    elif args.command == 'append'      : append_object(args, None)


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
            file_name: set()
        }
        index = json.dumps(index)
        binary_index = zlib.compress(index.encode())
        repo_index = './repos/{}/{}/{}'.format(dir_name[0:2], dir_name[2:], 'index')
        with open(repo_index, 'wb') as f:
            f.write(binary_index)
    else:
        raise Exception('Repo already exists!')


def read_root_object(args):
    dir_name = hashlib.sha1(args.path.encode()).hexdigest()
    repo_index = './repos/{}/{}/{}'.format(dir_name[0:2], dir_name[2:], 'index')
    if os.path.exists(repo_index):
        with open(repo_index, 'rb') as f:
            binary_index = f.read()
            index = zlib.decompress(binary_index)
            index = json.loads(index)
            root_filename = index['root']
            root_object = './repos/{}/{}/objects/{}'.format(dir_name[0:2], dir_name[2:], root_filename)
            with open(root_object, 'rb') as f:
                data = zlib.decompress(f.read())
                print(data.decode())
    else:
        raise Exception('Repo does not exist!')


def get_current_file_hash(path):
    index = repo_index(path)
    return index['current']


def get_hash(data):
    return hashlib.sha1(data.encode()).hexdigest()


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
    repo_objects_dir = os.path.join(repo, 'objects/')
    return repo_objects_dir


def write_repo_index(path, json_data):
    with open(repo_index_path(path), 'wb') as f:
        data = json.dumps(json_data)
        binary_data = zlib.compress(data.encode())
        f.write(binary_data)


def write_repo_object(path, obj):
    with open(os.path.join(repo_objects_path(path), obj), 'wb') as f:
        data = zlib.compress(obj.encode())
        f.write(data)


def append_object(path, file_hash, parent):
    index = repo_index(path)
    if parent != file_hash:
        index[parent].add(file_hash)
        index['current'] = file_hash
        if file_hash not in index:
            index[file_hash] = set()
        write_repo_index(path, index)
        write_repo_object(path, file_hash)
