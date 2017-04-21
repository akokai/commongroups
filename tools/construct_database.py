# coding: utf-8

"""
Create a chemical structure-searchable database for use with Common Groups.

This script creates a chemical database with ~720,000 structures from the
U.S. Environmental Protection Agency's CompTox Dashboard public dataset.

Set up the database so that it can be used for substructure searching via the
RDKit PostgreSQL database `extension`_. Also include CASRNs and PubChem CIDs as
much as possible.

Requirements:
-   A running instance of PostgreSQL and an empty initialized database with
    the RDKit extension activated. See Common Groups installation instructions.
-   Downloaded copies of certain data from the US EPA `CompTox Dashboard`_.
    Retrieve automatically with the ``download_epa.sh`` script.
-   Python dependencies: rdkit, sqlalchemy, psycopg2, pandas.

.. _extension: http://www.rdkit.org/docs/Cartridge.html
.. _CompTox Dashboard: https://comptox.epa.gov/dashboard/downloads
"""

import argparse
import os
from os.path import join as pjoin
import sys

import pandas as pd

from rdkit import Chem

from sqlalchemy import create_engine, text, types
from sqlalchemy.exc import ArgumentError


def construct_db(con, data_path):
    """
    Construct database using US EPA chemical datasets and the RDKit extension.
    """
    dtx_mapping = pjoin(data_path, 'dsstox_20160701.tsv')
    dtx_casrn_mapping = pjoin(data_path, 'Dsstox_CAS_number_name.xlsx')
    dtx_pubchem_mapping = pjoin(data_path, 'PubChem_DTXSID_mapping_file.txt')

    print('==> Creating tables.')
    con.execute(text(
        """
        CREATE TABLE dsstox (
            dtxsid text PRIMARY KEY,
            inchi text NOT NULL,
            inchikey text NOT NULL,
            bin bytea NOT NULL
        );

        CREATE TABLE dtx_casrn (
            casrn text,
            dtxsid text REFERENCES dsstox,
            name text,
            PRIMARY KEY (dtxsid, casrn)
        );

        CREATE TABLE dtx_cid (
            cid text,
            dtxsid text REFERENCES dsstox,
            PRIMARY KEY (dtxsid, cid)
        );
        """
    ))

    # Generate table of binary structural representations
    #####################################################
    # - Take the list of EPA InChI(Key)s and DSSTox substance IDs, convert
    #   each InChI into a RDKit `Mol` object. Then convert each `Mol` into
    #   its binary representation. Put this into a PostgreSQL database table.
    # - Update the table to create RDKit `mol` objects in a new column, using
    #   the binary representations and the `mol_from_pkl` function. Drop the
    #   binary column after this is complete.
    # - This binary step is necessary because there is no `mol_from_inchi`
    #   method in the PostgreSQL RDKit extension. (If there were, we could go
    #   straight from InChI to molecules in the SQL table).

    # Notes:
    # - The 720K rows seems to be too much to process in memory all at once,
    #   so we go through the file lazily in chunks.
    # - RDKit will fail to create many of the molecules from InChI because of
    #   very specific errors. The number of molecules we have in the end will
    #   probably be less than 720K.
    # - This will take a while and consume a lot of CPU and memory resources.

    print('==> Generating molecular structures from InChI strings...')
    dtypes = {'dtxsid': types.Text,
              'inchi': types.Text,
              'inchikey': types.Text,
              'bin': types.Binary}

    ninput = 719996
    ncreated = 0
    chunk = 10000

    dtx = pd.read_table(dtx_mapping,
                        names=['dtxsid', 'inchi', 'inchikey'],
                        chunksize=chunk,
                        low_memory=True)

    for frame in dtx:
        frame['mol'] = frame.inchi.apply(Chem.MolFromInchi)
        frame.dropna(inplace=True)
        num = len(frame)
        ncreated += num
        print('==> {0} molecules created, {1} errors'.format(num, chunk - num))
        frame['bin'] = frame.mol.apply(lambda m: m.ToBinary())
        frame.drop('mol', axis=1, inplace=True)
        frame.to_sql('dsstox',
                     con,
                     if_exists='append',
                     index=False,
                     chunksize=65536,
                     dtype=dtypes)

    print('==> Total: {0} molecules created, {1} errors'.format(
        ncreated, ninput - ncreated))

    # Generate `mol`-type column and drop binary column
    print('==> Regenerating molecular structures in the database table.')
    con.execute(text(
        """
        ALTER TABLE dsstox ADD COLUMN molecule mol;

        UPDATE dsstox SET molecule = mol_from_pkl(bin);

        ALTER TABLE dsstox ALTER COLUMN molecule SET NOT NULL;

        ALTER TABLE dsstox DROP COLUMN bin;
        """
    ))

    nmols = con.execute(text('select count(molecule) from dsstox;')).scalar()

    # Check results. The AssertionError should not happen.
    try:
        assert nmols == ncreated
    except AssertionError:
        print('==> WARNING: Discrepancy in number of molecules:'
              ' {0} input, {1} retrieved.'.format(ncreated, nmols))

    # Create DataFrame of DTXSIDs for which we have molecules in the database.
    # This will be used to avoid violations of foreign key constraints.
    ids = pd.read_sql("SELECT dtxsid FROM dsstox", con)

    # Import external ID mappings: DTXSID to CASRN, CID
    ###################################################
    # Load DTXSID:CASRN mappings. Note that these are all 1:1 mappings.
    dtx_cas_data = pd.read_excel(dtx_casrn_mapping)
    cas_cols = ['casrn', 'dtxsid', 'name']
    dtx_cas_data.columns = cas_cols
    print('==> {} DTXSID:CASRN mappings in data source'.format(
        len(dtx_cas_data)))

    # Filter mappings to include only DTXSIDs for which we already have a
    # molecule in the database.
    dtx_cas_data = dtx_cas_data.loc[dtx_cas_data['dtxsid'].isin(ids['dtxsid'])]
    print('==> {} DTXSID:CASRN mappings available to add to database'.format(
        len(dtx_cas_data)))

    dtypes_cas = dict(zip(cas_cols, 3*[types.Text]))
    dtx_cas_data.to_sql('dtx_casrn',
                        con,
                        if_exists='append',
                        index=False,
                        chunksize=65536,
                        dtype=dtypes_cas)

    nrows = con.execute(text('select count(*) from dtx_casrn;')).scalar()
    print('==> {} DTXSID-CASRN mappings added to database'.format(nrows))

    # Load DTXSID:CID mappings.
    # Each DTXSID is mapped onto one CID but non-uniquely (some share the same
    # CID). Dropping SIDs entirely, to simplify the database.
    dtx_cid_data = pd.read_table(dtx_pubchem_mapping, dtype=str)
    dtx_cid_data.drop('SID', axis=1, inplace=True)
    dtx_cid_data.drop_duplicates(inplace=True)  # Just to be safe
    cid_cols = ['cid', 'dtxsid']
    dtx_cid_data.columns = cid_cols
    print('==> {} DTXSID-CID mappings in data source'.format(
        len(dtx_cid_data)))

    # Filter mappings to include only DTXSIDs for which we already have a
    # molecule in the database.
    dtx_cid_data = dtx_cid_data.loc[dtx_cid_data['dtxsid'].isin(ids['dtxsid'])]
    print('==> {} DTXSID-CID mappings available to add to database'.format(
        len(dtx_cid_data)))

    dtypes_cid = dict(zip(cid_cols, 2*[types.Text]))
    dtx_cid_data.to_sql('dtx_cid',
                        con,
                        if_exists='append',
                        index=False,
                        chunksize=65536,
                        dtype=dtypes_cid)

    nrows = con.execute(text('select count(*) from dtx_cid;')).scalar()
    print('==> {} DTXSID-CID mappings added to database'.format(nrows))

    # Create view of all molecules and IDs
    ######################################
    create_view = text(
        """
        CREATE MATERIALIZED VIEW compounds
        AS SELECT
            dsstox.dtxsid,
            dsstox.inchi,
            dsstox.inchikey,
            dsstox.molecule,
            dtx_cid.cid,
            dtx_casrn.casrn,
            dtx_casrn.name
        FROM dsstox
        LEFT OUTER JOIN dtx_cid ON dtx_cid.dtxsid = dsstox.dtxsid
        LEFT OUTER JOIN dtx_casrn ON dtx_casrn.dtxsid = dsstox.dtxsid;
        """
    )
    res = con.execute(create_view)
    print('==> {} rows in combined view of compounds'.format(res.rowcount))
    cid_null = con.execute(text(
        'SELECT COUNT(*) FROM compounds where cid is null;')).scalar()
    print('  --> {} rows without CID'.format(cid_null))
    casrn_null = con.execute(text(
        'SELECT COUNT(*) FROM compounds where casrn is null;')).scalar()
    print('  --> {} rows without CASRN'.format(casrn_null))

    # Create the index
    print('==> Creating index...')
    cmd = text('CREATE INDEX molidx ON compounds USING gist(molecule);')
    res = con.execute(cmd)


def create_parser():
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-u',
                        '--db_url',
                        help='database URL',
                        required=True)
    parser.add_argument('-d',
                        '--data_path',
                        help='path to data sources',
                        required=True)
    return parser


def main():
    """Create structure-searchable database for use with Common Groups."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        con = create_engine(args.db_url)
        data_path = os.path.abspath(args.data_path)
        assert os.path.isdir(data_path)
    except ArgumentError:
        print('==> Failed to create database connection. Exiting.')
        sys.exit(1)
    except AssertionError:
        print('==> Path to data is not a directory or does not exist.')
        sys.exit(1)

    print('CONSTRUCT DATABASE FOR COMMONGROUPS',
          '===================================',
          '==> You will now see many warnings and errors.'
          ' It is OK to ignore most of them.',
          '==> Messages from this program begin with arrows.\n',
          sep='\n')

    construct_db(con, data_path)
    print('==> Done.\n')


if __name__ == '__main__':
    main()
