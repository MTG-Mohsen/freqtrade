# pragma pylint: disable=attribute-defined-outside-init

"""
This module load custom objects
"""
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Optional, Type, Any

logger = logging.getLogger(__name__)


class IResolver(object):
    """
    This class contains all the logic to load custom classes
    """

    @staticmethod
    def _get_valid_object(object_type, module_path: Path,
                          object_name: str) -> Optional[Type[Any]]:
        """
        Returns the first object with matching object_type and object_name in the path given.
        :param object_type: object_type (class)
        :param module_path: absolute path to the module
        :param object_name: Class name of the object
        :return: class or None
        """

        # Generate spec based on absolute path
        spec = importlib.util.spec_from_file_location('unknown', str(module_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore # importlib does not use typehints

        valid_objects_gen = (
            obj for name, obj in inspect.getmembers(module, inspect.isclass)
            if object_name == name and object_type in obj.__bases__
        )
        return next(valid_objects_gen, None)

    @staticmethod
    def _search_object(directory: Path, object_type, object_name: str,
                       kwargs: dict = {}) -> Optional[Any]:
        """
        Search for the objectname in the given directory
        :param directory: relative or absolute directory path
        :return: object instance
        """
        logger.debug('Searching for %s %s in \'%s\'', object_type.__name__, object_name, directory)
        for entry in directory.iterdir():
            # Only consider python files
            if not str(entry).endswith('.py'):
                logger.debug('Ignoring %s', entry)
                continue
            obj = IResolver._get_valid_object(
                object_type, Path.resolve(directory.joinpath(entry)), object_name
            )
            if obj:
                return obj(**kwargs)
        return None
