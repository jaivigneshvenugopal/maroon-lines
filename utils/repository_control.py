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

INDEX_HEAD = 'head'
INDEX_ROOT = 'root'
INDEX_ADOPTS = 'adopts'


def init_repo(file_path, file_data):
    """
    Create a new repo to kickstart tracking for a new file.

    :param file_path: full file location (inclusive of name and extension)
    :param file_data: file content
    :return: None
    """
    if not os.path.exists(file_path):
        raise Exception('Unable to initialise repo: Invalid path given')

    if repo_exists(file_path):
        raise Exception('Unable to initialise repo: Repo already exists')

    os.makedirs(repo_file_objects_path(file_path))

    # Three ingredients needed for a new repo directory
    write_repo_key(file_path)
    write_repo_file_object(file_path, file_data)
    write_repo_index(file_path, build_index_dict(file_data))


def copy_repo(old_file_path, new_file_path):
    """
    Copy a repo from one location to another.

    :param old_file_path: full file location (inclusive of name and extension)
    :param new_file_path: full file location (inclusive of name and extension)
    :return: None
    """
    if not old_file_path or not new_file_path:
        raise Exception('Unable to copy repo: Invalid path/s given')

    if old_file_path == new_file_path:
        return

    # Remove any lingering repo in the new location
    remove_repo(new_file_path)

    shutil.copytree(repo_path(old_file_path), repo_path(new_file_path))

    # Update repo key in the new location
    write_repo_key(new_file_path)


def move_repo(old_file_path, new_file_path):
    """
    Move a repo from one location to another.

    :param old_file_path: full file location (inclusive of name and extension)
    :param new_file_path: full file location (inclusive of name and extension)
    :return: None
    """
    copy_repo(old_file_path, new_file_path)
    remove_repo(old_file_path)


def remove_repo(file_path):
    """
    Remove a repo.

    :param file_path: full file location (inclusive of name and extension)
    :return: None
    """
    if not repo_exists(file_path):
        return

    shutil.rmtree(repo_path(file_path))


def rebuilt_repo(file_path, file_data):
    """
    Remove an existing repo and initialise a new one.

    :param file_path: full file location (inclusive of name and extension)
    :param file_data: file contents
    :return: None
    """
    remove_repo(file_path)
    init_repo(file_path, file_data)


def repo_exists(file_path):
    """
    Check if a repo exists.

    :param file_path: full file location (inclusive of name and extension)
    :return: Boolean representing existence of repo
    """
    return os.path.exists(repo_path(file_path))


def repo_path(file_path):
    """
    Return repo location.

    :param file_path: full file location (inclusive of name and extension)
    :return: Location of repo in string format
    """
    file_path_hash = get_hash(file_path)
    return os.path.join(REPOS, file_path_hash[0:2], file_path_hash[2:])


def repo_key_path(file_path):
    """
    Return location of a file named 'key' in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: Location of 'key' file in repo directory - in string format
    """
    return os.path.join(repo_path(file_path), KEY)


def repo_index_path(file_path):
    """
    Return location of a file named 'index' in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: Location of 'index' file in repo directory - in string format
    """
    return os.path.join(repo_path(file_path), INDEX)


def repo_file_objects_path(file_path):
    """
    Return location of a folder named 'objects' in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: Location of objects folder in repo directory - in string format
    """
    return os.path.join(repo_path(file_path), OBJECTS)


def repo_key(file_path):
    """
    Return 'key' object in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: 'key' object
    """
    with open(repo_key_path(file_path), 'r') as f:
        key = f.read()
    return key


def write_repo_key(file_path):
    """
    Write file_path to a file named 'key' in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: None
    """
    with open(repo_key_path(file_path), 'w') as f:
        f.write(file_path)


def repo_index(file_path):
    """
    Return 'index' object in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :return: 'index' object
    """
    with open(repo_index_path(file_path), 'rb') as f:
        binary_index = f.read()
        json_index = zlib.decompress(binary_index)
        dict_index = json.loads(json_index)
    return dict_index


def write_repo_index(file_path, dict_index):
    """
    Write dict_index to file named 'index' in repo directory.

    :param file_path: full file location (inclusive of name and extension)
    :param dict_index: a python dict object
    :return: None
    """
    with open(repo_index_path(file_path), 'wb') as f:
        json_index = json.dumps(dict_index)
        binary_index = zlib.compress(json_index.encode())
        f.write(binary_index)


def repo_index_head(file_path):
    """
    Return head file object in index.

    :param file_path: full file location (inclusive of name and extension)
    :return: hash of the head file object
    """
    index = repo_index(file_path)
    return index[INDEX_HEAD]


def update_repo_index_head(file_path, file_hash):
    """
    Update head and re-write repo index.

    :param file_path: full file location (inclusive of name and extension)
    :param file_hash: hash that represents file content
    :return: None
    """
    index = repo_index(file_path)
    index[INDEX_HEAD] = file_hash
    write_repo_index(file_path, index)


def build_index_dict(file_data):
    """
    Create a new python dict object called index.

    :param file_data: file content
    :return: python dict object
    """
    file_hash = get_hash(file_data)
    index = {
        INDEX_ROOT: file_hash,
        INDEX_HEAD: file_hash,
        INDEX_ADOPTS: [],
        file_hash: []
    }
    return index


def repo_file_object(file_path, file_hash):
    """
    Decompress file object and return file content.

    :param file_path: full file location (inclusive of name and extension)
    :param file_hash: Hash of file content
    :return: file content
    """
    with open(repo_file_object_path(file_path, file_hash), 'rb') as f:
        binary_file_data = f.read()
        encoded_file_data = zlib.decompress(binary_file_data)
        file_data = encoded_file_data.decode()
    return file_data


def repo_file_object_path(file_path, file_hash):
    """
    Return location of a certain file object.

    :param file_path: full file location (inclusive of name and extension)
    :param file_hash: Hash of file content
    :return: path of file object
    """
    return os.path.join(repo_file_objects_path(file_path), file_hash)


def repo_file_object_exists(file_path, file_hash):
    """
    Check if file object exists.

    :param file_path: full file location (inclusive of name and extension)
    :param file_hash: Hash of file content
    :return: Boolean representing existence of file object
    """
    return os.path.exists(repo_file_object_path(file_path, file_hash))


def write_repo_file_object(file_path, file_data):
    """
    Write a file object.

    :param file_path: full file location (inclusive of name and extension)
    :param file_data: file content
    :return: None
    """
    file_hash = get_hash(file_data)
    with open(repo_file_object_path(file_path, file_hash), 'wb') as f:
        binary_file_data = zlib.compress(file_data.encode())
        f.write(binary_file_data)


def add_file_object_to_index(file_path, file_data, adopted=False):
    """
    Add a new file object to index.

    :param file_path: full file location (inclusive of name and extension)
    :param file_data: file content
    :param adopted: Boolean representing if the relationship is not natural
    :return: None
    """
    index = repo_index(file_path)
    file_hash = get_hash(file_data)
    parent_file_hash = index[INDEX_HEAD]

    index[parent_file_hash].append(file_hash)
    index[INDEX_HEAD] = file_hash

    if file_hash not in index:
        index[file_hash] = []

    if adopted:
        index[INDEX_ADOPTS].append((parent_file_hash, file_hash))

    write_repo_index(file_path, index)
    write_repo_file_object(file_path, file_data)


def get_hash(file_data):
    """
    Get hash of file content.

    :param file_data: file content
    :return: hash of file content
    """
    return hashlib.sha1(file_data.encode()).hexdigest()
