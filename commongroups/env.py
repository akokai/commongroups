# coding: utf-8

"""Environment for compound group operations."""

from datetime import datetime
import json
import logging
import os
from os.path import join as pjoin

from boltons.fileutils import mkdir_p
from sqlalchemy import create_engine

from commongroups.errors import MissingParamError
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def add_project_handler(log_file):
    """
    Add a project-specific :class:`FileHandler` for all logging output.

    This enables logging to a file that's kept within the project
    directory.
    """
    loggers = list(logconf.CONFIG['loggers'].keys())
    proj_handler = logging.FileHandler(log_file, mode='w')
    fmt = logging.getLogger('commongroups').handlers[0].formatter
    proj_handler.setFormatter(fmt)
    for item in loggers:
        lgr = logging.getLogger(item)
        lgr.addHandler(proj_handler)


class CommonEnv(object):
    """
    Run environment for :mod:`commongroups`.

    This object keeps track of a project environment (i.e., file locations
    for data and logs, shared parameters), which can be used by instances of
    :class:`CMGroup` or by a number of functions needing such information.

    Instantiating this class creates a directory tree: the project directory
    corresponding to ``project_path`` and subdirectories ``data``, ``log``, and
    ``results``. The project directory is created within the "home" directory
    corresponding to ``env_path``.  A new log file is created in the ``log``
    subdirectory each time a new ``CommonEnv`` with the same project name is
    created.

    Parameters:
        name (str): Project name, used to name the project directory.
        env_path (str): Path to root commongroups home. If not specified,
            looks for environment variable ``CMG_HOME`` or defaults to
            ``~/commongroups_data``.
        kwargs: Configuration options to override those read from file.
    """
    def __init__(self,
                 name=None,
                 env_path=None,
                 **kwargs):
        if env_path:
            self._env_path = os.path.abspath(env_path)
        elif os.getenv('CMG_HOME'):
            self._env_path = os.path.abspath(os.getenv('CMG_HOME'))
        else:
            self._env_path = pjoin(os.path.expanduser('~'),
                                   'commongroups_data')

        self._name = name or 'default'
        self._project_path = pjoin(self._env_path, self._name)
        mkdir_p(self._project_path)

        # Set up per-project logging to file.
        log_path = pjoin(self._project_path, 'log')
        mkdir_p(log_path)
        log_file = pjoin(log_path,
                         datetime.now().strftime('%Y%m%dT%H%M%S') + '.log')
        add_project_handler(log_file)

        # Set up data and results directories.
        self._data_path = pjoin(self._project_path, 'data')
        mkdir_p(self._data_path)
        self._results_path = pjoin(self._project_path, 'results')
        mkdir_p(self._results_path)
        mkdir_p(pjoin(self._results_path, 'html'))

        # Log where the directories & files have been created.
        logger.info('Project path: %s', self._project_path)

        self.set_config(kwargs)
        self.database = None

    # The following attributes are read-only because changing them would
    # result in inconsitencies with file paths.
    @property
    def name(self):
        """Project name."""
        return self._name

    @property
    def project_path(self):
        """Path to project directory."""
        return self._project_path

    @property
    def data_path(self):
        """Path to the project data directory."""
        return self._data_path

    @property
    def results_path(self):
        """Path to the project results directory."""
        return self._results_path

    def __repr__(self):
        args = [self._name, self._env_path]
        return 'CommonEnv({})'.format(', '.join(args))

    def __str__(self):
        return 'CommonEnv({})'.format(self._name)

    def _read_config(self):
        """Load and return operating parameters from file, as a dict."""
        config_path = pjoin(self._env_path, 'config.json')
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
            logger.debug('Read config file: %s', config_path)
            return config
        except FileNotFoundError:
            logger.warning('No config file: %s', config_path)
            return

    def set_config(self, opts):
        """
        Combine config options from file and from object instantiation.

        Parameters passed as ``config`` when the ``CommonEnv`` was created will
        overwrite parameters read from file (individually).

        Parameters:
            opts (dict): Configuration options.
        """
        self.config = self._read_config() or dict()
        if opts and isinstance(opts, dict):
            self.config.update(opts)

    def connect_database(self):
        """Instantiate a SQLAlchemy engine for connecting to the database."""
        if 'database_url' not in self.config:
            raise MissingParamError('database_url')
        con = create_engine(self.config['database_url'])
        self.database = con
        return con
