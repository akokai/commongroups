Developer reference
===================

``env`` - Environment
---------------------

.. automodule:: commongroups.env
   :members:
   :show-inheritance:

``cmgroup`` - Compound group
----------------------------

.. automodule:: commongroups.cmgroup
   :members:
   :show-inheritance:

``query`` - Database queries
----------------------------

.. automodule:: commongroups.query
   :members:
   :show-inheritance:

``googlesheet`` - Google Sheets access
--------------------------------------

.. automodule:: commongroups.googlesheet
   :members:
   :show-inheritance:

``hypertext`` - Generating HTML output
--------------------------------------

.. automodule:: commongroups.hypertext
   :members:
   :show-inheritance:

``errors`` - Exceptions
-----------------------

.. automodule:: commongroups.errors
   :members:
   :show-inheritance:

``run`` - The run script
------------------------

See :doc:`usage`.

.. automodule:: commongroups.run
   :members:
   :show-inheritance:

Tests
-----

This package includes a suite of unit tests. Currently, the included tests only
cover the architecture of the program itself, and not the logic of SQL queries
against the database.

Tests can be run on the installed package using::

   pytest --pyargs commongroups

Or on the source code (without installing) by running::

   python setup.py test

For *all* of the tests to pass, you must have a :doc:`database <database>`
already set up, the PostgreSQL server must be running; your ``commongroups``
environment must be :ref:`configured <config>` to allow the program to access
this database *and* to access a :ref:`Google Spreadsheet <googlesetup>`
containing test parameters. Please contact the authors if you want to run tests
yourself and would like a sample spreadsheet.
