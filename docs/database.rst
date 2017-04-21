Database
========

For ``commongroups`` to work, it needs a database of compounds searchable
by chemical structure. We do not distribute a pre-built database, and there are
no requirements for or limits on what compounds and data sources might be
included in the database.

We develop and test ``commongroups`` using a database compiled from public data
available in the `US EPA CompTox Dashboard`_, containing approximately 700,000
structures. We believe that this is a good starting point for our immediate
goals. We distribute a program that can :ref:`automatically <autodb>` download
data and recreate the particular database that we use.

What follows is a general description of how a database can be created and
prepared for use with ``commongroups``.

.. _datasources:

Data sources
------------

From the `US EPA CompTox Dashboard`_:

-  ``dsstox_20160701.tsv``
   -  Downloaded as ``DSSTox_Mapping_20160701.zip``

   -  Date: 2016-07-01 (file generated); 2016-12-14 (posted on EPA website)

   -  Accessed: 2017-04-18

   -  Contains mappings between the DSSTox substance identifier (DTXSID)
      and the associated InChI/InChIKey.

-  ``Dsstox_CAS_number_name.xlsx``

   -  Date: 2016-11-14

   -  Accessed: 2017-04-18

   -  Contains the CASRN, DTXSID, and the "preferred name" used by US EPA.

-  ``PubChem_DTXSID_mapping_file.txt``

   -  Date: 2016-11-14

   -  Accessed: 2017-04-18

   -  Contains the PubChem SID, PubChem CID and DTXSID.


Constructing the database
-------------------------

These are the general steps to create the database using the data sources
above:

1. Create a database table of DTXSIDs, InChI(Key)s, and RDKit ``mol``-type
   representations of the structures (based on InChI)

2. Create database tables with DTXSID-CASRN and DTXSID-CID correspondences.

3. Merge the above tables on DTXSID, creating either a new table or a
   materialized view. Create an index on molecular structures using the
   GiST-powered RDKit extension.

**To execute these steps automatically** on your system, first :doc:`install
<install>` the required software and then see :ref:`autodb`. For more technical
detail and the exact database commands used, please see the source code in
``tools/construct_database.py``.

Known limitations
-----------------

Currently, for ``commongroups`` to be able to use a database, it must contain a
table or view called ``compounds``, which in turn must contain a column called
``molecule``, containing molecular structures in the RDKit ``mol`` data type.
Furthermore, for HTML display of compound groups, the program currently assumes
that there is a ``cid`` column in ``compounds`` containing the PubChem CID for
each substance.

The database produced by our automatic installation script satisfies these
requirements.

.. _US EPA CompTox Dashboard: https://comptox.epa.gov/dashboard/downloads
