import sys
import os
import site
import logging

_logger = logging.getLogger(__name__)

# Path to the lib directory
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')

# Logging the current lib path
_logger.info("lib_path: %s", lib_path)

# Adding each subdirectory in lib_path to sys.path
for subdir in os.listdir(lib_path):
    full_subdir_path = os.path.join(lib_path, subdir)
    if os.path.isdir(full_subdir_path):
        site.addsitedir(full_subdir_path)
        sys.path.append(full_subdir_path)
        _logger.info("Added to sys.path: %s", full_subdir_path)

_logger.info("Added lib_path to sys.path: %s", lib_path)
_logger.info("Current sys.path: %s", sys.path)

# Import models after setting up the paths
from . import models