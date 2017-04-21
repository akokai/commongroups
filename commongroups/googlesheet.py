# coding: utf-8

"""
Get compound group parameters from a Google Sheet.

See :ref:`Google Sheets access <googlesetup>` for more information.
"""

from itertools import islice
import json
import logging
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC

from commongroups.cmgroup import CMGroup, BASE_PARAMS
from commongroups.errors import NoCredentialsError
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

SCOPE = ['https://spreadsheets.google.com/feeds']


class SheetManager(object):
    """
    Object to manage Google Sheets access.

    Parameters:
        key_file (str): Path to Google service account credentials
            JSON file.
        title (str): *Title* of the Google Sheet to open.
        worksheet (str): Title of the *worksheet* containing parameters
            within the Google Sheet.

    Raises:
        :class:`commongroups.errors.NoCredentialsError`: If the API
            credentials are missing or cannot be parsed from JSON.

    Notes:
        Yes, we open Google Sheets *by title.*  It would be nice to open them
        by key or by URL, but that functionality in :mod:`gspread` is broken
        because of the "New Sheets".
    """
    def __init__(self, title, worksheet, key_file):
        _key_file = os.path.abspath(key_file)
        try:
            creds = SAC.from_json_keyfile_name(_key_file, SCOPE)
        except FileNotFoundError:
            raise NoCredentialsError(_key_file)
        logger.debug('Authorizing Google Service Account credentials')
        self._google = gspread.authorize(creds)
        self.title = title
        self.spreadsheet = None
        self.worksheet = worksheet

    def get_spreadsheet(self):
        """
        Open the spreadsheet containing CMG parameters.

        Returns:
            :class:`gspread.Spreadsheet`: The Google Sheet object.
        """
        if not self.spreadsheet:
            logger.debug('Opening Google Sheet by title: %s', self.title)
            self.spreadsheet = self._google.open(self.title)
        return self.spreadsheet

    def get_params(self):
        """
        Read parameters and info from spreadsheet rows iteratively.

        Stops reading the spreadsheet when a blank row is encountered.

        Yields:
            Parameters and info for each group (row), as nested dicts.
        """
        doc = self.get_spreadsheet()
        logger.debug('Getting worksheet by title: %s', self.worksheet)
        wks = doc.worksheet(self.worksheet)

        npars = len(BASE_PARAMS)
        ikeys = wks.row_values(1)[npars:]

        for i in range(2, wks.row_count + 1):
            if not any(wks.row_values(i)):
                raise StopIteration
            vals = wks.row_values(i)
            params = {k: v for (k, v) in zip(BASE_PARAMS, vals[:npars])}
            info = {k: v for (k, v) in zip(ikeys, vals[npars:])}
            yield {'params': params, 'info': info}

    def get_cmgs(self, env):
        """
        Generate :class:`CMGroup` objects from parameters in spreadsheet rows.

        Parameters:
            env (:class:`commongroups.env.CommonEnv`): The project environment
                that the returned objects will use to store data, etc.

        Yields:
            :class:`CMGroup` objects based on parameters in each row.
        """
        logger.debug('Generating CMGs from worksheet: %s', self.worksheet)

        for item in self.get_params():
            yield CMGroup(env, item['params'], item['info'])

    def params_to_json(self, path):
        """
        Get group parameters from the worksheet and output to a JSON file.

        Parameters:
            path: Path to output file.
        """
        group_params = list(islice(self.get_params(), None))
        path = os.path.abspath(path)
        logger.debug('Writing parameters to file: %s', path)
        with open(path, 'w') as json_file:
            json.dump(group_params, json_file, indent=2, sort_keys=True)
