# coding: utf-8

"""Common Groups operations."""

from os.path import abspath, join as pjoin
import logging
import json

from commongroups.cmgroup import CMGroup
from commongroups.errors import MissingParamError, NoCredentialsError
from commongroups.googlesheet import SheetManager
from commongroups.hypertext import directory
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def cmgs_from_googlesheet(env):
    """
    Generate compound group objects from parameters given in a Google Sheet.

    Use the Google Sheets source referenced in the environment's configuration.

    Parameters:
        env (:class:`commongroups.env.CommonEnv`): Environment to use for all
            generated groups and for identifying the Google Sheet.

    Returns:
        Generator yielding :class:`commongroups.cmgroup.CMGroup` objects.
    """
    logger.info('Generating compound groups from Google Sheet')
    try:
        sheet = SheetManager(env.config['google_sheet_title'],
                             env.config['google_worksheet'],
                             env.config['google_key_file'])
    except KeyError as keyx:
        logger.exception('Google Sheets access is not configured')
        raise MissingParamError(keyx.args[0])
    except NoCredentialsError:
        logger.exception('Cannot authenticate Google Service Account')
        raise
    cmg_gen = sheet.get_cmgs(env)
    return cmg_gen


# TODO: Import group definitions from spreadsheet file.
def cmgs_from_file(env, path, filetype=None):
    """
    Generate compound group objects from a file.

    Only the defining parameters and descriptive information for each compound
    group are imported from the file. Importing lists of compounds for already
    populated groups is *not supported.*

    Parameters:
        env (:class:`commongroups.env.CommonEnv`): The project environment.
            Determines the environment used for the :class:`CMGroup` objects.
        path (str): Path to a file containing parameters, and optionally
            other ``info``, for a number of CMGs.
        filetype (str): Type of file; required only if path does not have a
            file extension.

    Yields:
        :class:`commongroups.cmgroup.CMGroup` objects.
    """
    filetype = filetype or path.split('.')[-1]
    filetype = filetype.lower()
    path = abspath(path)
    logger.debug('Reading group parameters from %s', path)
    if filetype == 'json':
        with open(path, 'r') as json_file:
            many_params = json.load(json_file)
    else:
        raise NotImplementedError(
            'File type unsupported: {}'.format(filetype))
    for item in many_params:
        yield CMGroup(env, item['params'], item['info'])


def collect_to_json(cmgs, env, filename=None):
    """
    Write parameters and info for a number of compound groups to a JSON file.

    The output is written to ``cmgroups.json`` (or other filename if specified)
    in the project environment's ``results`` directory.

    Parameters:
        cmgs (iterable): :class:`commongroups.cmgroup.CMGroup` objects to write.
        env (:class:`commongroups.env.CommonEnv`): Project environment.
        filename (str): Optional alternative filename.
    """
    filename = filename or 'cmgroups.json'
    cmg_data = [cmg.to_dict() for cmg in cmgs]
    path = pjoin(env.results_path, filename)
    logger.info('Writing JSON file: %s', path)
    with open(path, 'w') as json_file:
        json.dump(cmg_data, json_file, indent=2, sort_keys=True)


def batch_process(cmgs, env):
    """
    Process compound groups in a given environment and output all results.

    Use the database connection provided by the environment. Output results to
    Excel (compound lists and group info) and JSON (group parameters and info).
    Create a browseable HTML directory of all groups & results.

    Parameters:
        cmgs (iterable): :class:`commongroups.cmgroup.CMGroup` objects to
            process.
        env (:class:`commongroups.env.CommonEnv`): Environment.

    Returns:
        List of processed compound groups.
    """
    if not env.database:
        env.connect_database()

    processed_cmgs = []

    for cmg in cmgs:
        cmg.process(env.database)
        cmg.to_excel()
        cmg.to_json()
        cmg.to_html(formats=['xlsx', 'json'])
        processed_cmgs.append(cmg)

    collect_to_json(processed_cmgs, env)
    directory(processed_cmgs, env)
    return processed_cmgs
