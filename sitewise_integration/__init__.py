import sys
import os
import site
import logging

# Logging setup to debug issues with loading libraries
_logger = logging.getLogger(__name__)

# Path to the lib directory
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')

# Verify if the lib_path exists and is a directory
if not os.path.isdir(lib_path):
    _logger.error("Library path %s does not exist or is not a directory", lib_path)
else:
    _logger.info("Looking for libraries in: %s", lib_path)

    # Adding each subdirectory in lib_path to sys.path
    for subdir in os.listdir(lib_path):
        full_subdir_path = os.path.join(lib_path, subdir)
        if os.path.isdir(full_subdir_path):
            try:
                # Use site.addsitedir to add the site-specific directory to sys.path
                site.addsitedir(full_subdir_path)
                # Explicitly append to sys.path as well
                sys.path.append(full_subdir_path)
                _logger.info("Added %s to sys.path", full_subdir_path)
            except Exception as e:
                _logger.error("Error adding %s to sys.path: %s", full_subdir_path, e)

# Final check of sys.path
_logger.info("Final sys.path: %s", sys.path)

# Check if boto3 can be imported
try:
    import boto3
    _logger.info("Boto3 successfully imported.")
except ImportError as e:
    _logger.error("Error importing boto3: %s", e)

# Import models after setting up sys.path
from . import models