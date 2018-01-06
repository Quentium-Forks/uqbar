"""
Tools for IO and file-system manipulation.
"""

import collections
import pathlib
from typing import Sequence, Union

from .DirectoryChange import DirectoryChange  # noqa
from .Profiler import Profiler  # noqa
from .RedirectedStreams import RedirectedStreams  # noqa
from .Timer import Timer  # noqa


def walk(
    root_path: Union[str, pathlib.Path],
    top_down: bool=True,
    ) -> None:
    """
    Walks a directory tree.

    Like :py:func:`os.walk` but yielding instances of :py:class:`pathlib.Path`
    instead of strings.

    :param root_path: foo
    :param top_down: bar
    """
    root_path = pathlib.Path(root_path)
    directory_paths, file_paths = [], []
    for path in sorted(root_path.iterdir()):
        if path.is_dir():
            directory_paths.append(path)
        else:
            file_paths.append(path)
    if top_down:
        yield root_path, directory_paths, file_paths
    for directory_path in directory_paths:
        yield from walk(directory_path, top_down=top_down)
    if not top_down:
        yield root_path, directory_paths, file_paths


def write(
    contents: str,
    path: Union[str, pathlib.Path],
    verbose: bool=False,
    ) -> None:
    """
    Writes ``contents`` to ``path``.

    Checks if ``path`` already exists and only write out new contents if the
    old contents do not match.

    Creates any intermediate missing directories.

    :param contents: the file contents to write
    :param path: the path to write to
    :param verbose: whether to print output
    """
    path = pathlib.Path(path)
    if path.exists():
        with path.open('r') as file_pointer:
            old_contents = file_pointer.read()
        if old_contents == contents:
            if verbose:
                print('preserved: {}'.format(path))
            return False
        else:
            with path.open('w') as file_pointer:
                file_pointer.write(contents)
            if verbose:
                print('rewrote: {}'.format(path))
            return True
    elif not path.exists():
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        with path.open('w') as file_pointer:
            file_pointer.write(contents)
        if verbose:
            print('wrote: {}'.format(path))


def find_common_prefix(
    paths: Sequence[Union[str, pathlib.Path]]
    ) -> pathlib.Path:
    counter = collections.Counter()
    for path in paths:
        path = pathlib.Path(path).absolute()
        counter.update([path])
        counter.update(path.parents)
    paths = sorted([
        path for path, count in counter.items()
        if count >= len(paths)
        ], key=lambda x: len(x.parts))
    if paths:
        return paths[-1]


def relative_to(source_path, target_path):
    source_path = pathlib.Path(source_path).absolute()
    if source_path.is_file():
        source_path = source_path.parent
    target_path = pathlib.Path(target_path).absolute()
    common_prefix = find_common_prefix([source_path, target_path])
    if not common_prefix:
        raise ValueError('No common prefix')
    source_path = source_path.relative_to(common_prefix)
    target_path = target_path.relative_to(common_prefix)
    result = pathlib.Path(*['..'] * len(source_path.parts))
    return result / target_path