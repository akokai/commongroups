# coding: utf-8

"""Database querying methods for compound groups."""

import logging

from pandas import DataFrame

# import rdkit
# from rdkit import Chem, rdBase
# from rdkit.Chem import AllChem, Draw, rdqueries, rdMolDescriptors

from sqlalchemy import select, table, text  # and_, or_, not_

from commongroups.errors import MissingParamError
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# Names of database table & column containing searchable structures are
# hard-coded for now, but could be made part of CommonEnv config.
REL = 'compounds'
MOL = 'compounds.molecule'

REQUIRED_PARAMS = ['method', 'structure_type', 'structure']

TABLE = table(REL)


class QueryMethod(object):
    """
    Create, describe, and execute a query for populating a compound group.

    Parameters:
        params (dict): Compound group parameters of a :class:`CMGroup` object.
    """
    def __init__(self, params):
        self.params = params
        self.expression = None
        self.create_expression()

    def create_query_where(self):
        """Generate a query expression from a WHERE clause."""
        if 'code' not in self.params or not self.params['code']:
            raise MissingParamError('code')
        where_txt = self.params['code'].replace(':m', MOL)
        clause = text(where_txt).bindparams(s=self.params['structure'])
        que = select([text('*')]).select_from(TABLE).where(clause)
        self.expression = que

    def get_literal(self):
        """
        Return a string literal of the query expression, with bound parameters.
        """
        literal = str(
            self.expression.compile(compile_kwargs={'literal_binds': True})
        )
        return literal

    def create_expression(self):
        """
        Compose a SQLAlchemy expression based on the supplied parameters.

        Set object attribute ``expression``.
        """
        for req in REQUIRED_PARAMS:
            if req not in self.params or not self.params[req]:
                raise MissingParamError(req)

        if self.params['method'] == 'SQL':
            self.create_query_where()
        else:
            raise NotImplementedError(
                'Unsupported method: {}'.format(self.params['method']))
        self.get_literal()

    def describe(self):
        """
        Create a textual description of the query method with minimal HTML.
        """
        ret = ('This group is defined by a {0} query using'
               ' the {1} structure <code>{2}</code>.')
        ret = ret.format(self.params['method'],
                         self.params['structure_type'],
                         self.params['structure'])
        return ret

    def __call__(self, con):
        return get_query_results(self.expression, con)

    def __repr__(self):
        return 'QueryMethod({})'.format(repr(self.params))


def get_query_results(que, con):
    """
    Execute a database query using SQLAlchemy.

    Parameters:
        que: SQLAlchemy :class:`Select` object.
        con: SQLAlchemy database :class:`Connection` object.

    Returns:
        A pandas :class:`DataFrame` containing all rows of results.
    """
    res = con.execute(que)
    logger.info('%i results', res.rowcount)
    ret = DataFrame(res.fetchall(), columns=res.keys())
    return ret


# Previous attempts at factoring out query logic...
###################################################

# def substructure_query(pattern, mol, fields):
#     """
#     Construct a substructure query based on a SMARTS query molecule.

#     Parameters:
#         pattern: Substructure query molecule as SMARTS string.
#         mol: SQLAlchemy object representing a column of searchable molecules.
#         fields (iterable): SQLAlchemy selctable objects to select from.

#     Returns:
#         SQLAlchemy :class:`Select` object.
#     """
#     where_clause = mol.op('@>')(text(':q ::qmol').bindparams(q=str(pattern)))
#     que = select(fields).where(where_clause)
#     return que


# def substruct_exclude(pattern, excludes, mol, fields):
#     """
#     Construct a query matching one substructure and excluding others.

#     Parameters:
#         pattern (str): Substructure to match, as a SMARTS string.
#         excludes (iterable): Substructures to exclude, as SMARTS strings.
#         mol: SQLAlchemy object representing a column of searchable molecules.
#         fields (iterable): SQLAlchemy selctable objects to select from.

#     Returns:
#         SQLAlchemy :class:`Select` object.
#     """
#     sub_clause = mol.op('@>')(text(':p ::qmol').bindparams(p=pattern))
#     not_clauses = []
#     for pat in excludes:
#         match = mol.op('@>')(text(':x ::qmol').bindparams(x=pat))
#         not_clauses.append(not_(match))
#     que = select(fields).where(and_(sub_clause, *not_clauses))
#     return que


# def get_element_inorganic(elem_smarts, mol, fields):
#     """
#     Match all compounds containing an element but exclude any compounds
#     containing C-H or C-C bonds. Works OK most of the time.
#     """
#     organic_smarts = ['[C,c]~[C,c]', '[C!H0,c!H0]']
#     return substruct_exclude(elem_smarts, organic_smarts, mol, fields)
