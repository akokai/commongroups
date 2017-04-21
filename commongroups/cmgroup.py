# coding: utf-8

"""Compound group class."""

from os.path import join as pjoin
import logging
import json

import pandas as pd
from pandas import DataFrame, ExcelWriter

from commongroups.query import QueryMethod
from commongroups.hypertext import cmg_to_html
from commongroups.errors import MissingParamError
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

BASE_PARAMS = [
    'cmg_id',
    'name',
    'method',
    'structure_type',
    'structure',
    'code'
]


class CMGroup(object):
    """
    Compound group object.

    Initialize with parameters (``params``), which are known in advance and
    assumed to stay unchanged. Call the :func:`create_query` method to set up a
    database query, then call :func:`process` (requires a database connection)
    to populate the object's ``compounds`` and ``info`` attributes.  Add your
    own annotations using :func:`add_info`.

    Data, output, and logs for each :class:`CMGroup` are managed using an
    associated :class:`CommonEnv` project environment. See :doc:`design`.

    Parameters:
        env (:class:`commongroups.env.CommonEnv`): The project environment.
        params (dict): A dictionary containing the parameters of the compound
            group. See :ref:`parameters`.
        info (dict): Optional extra information as key-value pairs.
    """
    def __init__(self, env, params, info=None):
        if 'cmg_id' not in params:
            logger.critical('Cannot initialize CMGroup without cmg_id')
            raise MissingParamError('cmg_id')
        self.params = params
        if info and isinstance(info, dict):
            self.info = info
        else:
            self.info = dict()
        self.data_path = env.data_path
        self.results_path = env.results_path
        self.query = None
        self._compounds = None
        logger.info('Created %s', self)

    def __repr__(self):
        return 'CMGroup({})'.format(self.params)

    def __str__(self):
        return 'CMGroup({})'.format(self.cmg_id)

    @property
    def cmg_id(self):
        """Compound group ID (convenience method to retrieve from params)."""
        return self.params['cmg_id']

    @property
    def name(self):
        """Compound group name (convenience method to retrieve from params)."""
        return self.params['name']

    @property
    def compounds(self):
        """
        If populated, return a ``DataFrame`` of compounds in the group.

        Warning: ``DataFrame`` objects are easily modified by accident. Making
        this a read-only attribute does not prevent accidental modification.
        """
        return self._compounds

    def add_info(self, info):
        """
        Add information to the group as key-value pairs.

        Parameters:
            data (dict): A dict containing any number of items.
        """
        self.info.update(info)

    def create_query(self):
        """
        Create query method based on compound group parameters.

        Add a callable :class:`commongroups.query.QueryMethod` attribute.
        """
        self.query = QueryMethod(self.params)
        self.query.create_expression()

    def process(self, con):
        """
        Execute the database query and store results in the ``CMGroup`` object.

        Populate the ``compounds`` list with query results; add a computed
        summary of results to the ``info`` attribute.

        Parameters:
            con (:class:`sqlalchemy.engine.Engine`): Database connection.
        """
        self.create_query()
        res = self.query(con)
        self.add_info({'about': self.query.describe(),
                       'sql': self.query.get_literal(),
                       'count': len(res)})
        self._compounds = res

    def to_dict(self):
        """Return a dict of ``CMGroup`` parameters and info."""
        ret = {'params': self.params, 'info': self.info}
        return ret

    def to_json(self, path=None):
        """Serialize ``CMGroup`` parameters and info as JSON."""
        if not path:
            path = pjoin(self.results_path, '{}.json'.format(self.cmg_id))
        logger.info('Writing JSON file: %s', path)
        with open(path, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=2, sort_keys=True)

    def to_html(self, *args, **kwargs):
        """
        Output HTML display of the compound group.

        For options see :func:`commongroups.hypertext.cmg_to_html`.
        """
        cmg_to_html(self, *args, **kwargs)

    def to_excel(self, path=None):
        """
        Output compound group data to an Excel spreadsheet.

        Parameters and info are tabulated on the first sheet, and the full
        compounds ``DataFrame`` is exported to the second sheet.
        """
        meta_frame = pd.concat(
            [DataFrame(self.params, columns=self.params.keys(),
                       index=['value']).transpose(),
             DataFrame(self.info, columns=self.info.keys(),
                       index=['value']).transpose()]
        )
        cpds_frame = self.compounds.copy()
        cpds_frame['cmg_id'] = self.cmg_id

        path = pjoin(self.results_path,
                     '{0}.xlsx'.format(self.cmg_id))
        logger.info('Writing Excel file: %s', path)
        with ExcelWriter(path) as writer:
            meta_frame.to_excel(writer,
                                sheet_name='params+info',
                                index_label='parameter')
            cpds_frame.to_excel(writer, sheet_name='compounds', index=False)

    # TODO: Ability to apply group definition logic to a single compound,
    #       not in the database. This would seem to call for abstracting the
    #       logic out of SQL...
    # def screen(self, compound):
    #     """Screen a compound for membership in the group."""
    # raise NotImplementedError
