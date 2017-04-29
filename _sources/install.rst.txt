Installation
============

Installing this software involves the following general steps: installing
`Python`_ version 3.5, the ``commongroups`` Python package, and all of its
software dependencies; initializing a PostgreSQL database and installing the
RDKit extension; building a structure-searchable database.

The recommended way to install Python is with the `Anaconda`_ Python
distribution, or the light-weight `Miniconda`_ distribution.  This has the
benefits of allowing installation of RDKit using the `conda`_ package manager,
and simultanously creating a separate Python environment for Common Groups
(which is highly recommended).

On :ref:`linux`, parts of the installation process can be done automatically
using a shell script that we provide.

Step by step
------------

Any system
^^^^^^^^^^

1. Install `Miniconda`_.

2. Create a new ``conda`` environment and install RDKit, then activate the
   new environment::

      conda create -n <name> -c rdkit rdkit cairocffi
      source activate <name>

   Where ``<name>`` is the name of the new conda environment to create (for
   example, ``cmg_env``).

3. Install the ``commongroups`` Python package and the rest of its software
   dependencies::

      pip install commongroups

4. Install `PostgreSQL`_. Initialize a PostgreSQL database and install the
   RDKit extension. See specific installation instructions for
   `RDKit/PostgreSQL`_ on your operating system.

.. _linux:

Linux systems
^^^^^^^^^^^^^

1. Install `Miniconda`_.

2. Clone or download the Common Groups `repository`_.

3. Run the provided shell script to install all software dependencies *and*
   initialize a PostgreSQL database with the RDKit extension::

      bash tools/install_deps.sh -n <name> -d <datadir>

   Where ``<name>`` is the name of the new conda environment to create (for
   example, ``cmg_env``), and ``<datadir>`` is the path to a directory which
   shall be used as the PostgreSQL data directory.

   Make note of the database URL and instructions for starting/stopping the
   database server, which will be displayed if the install is successful.


.. _autodb:

Automated database instantiation
--------------------------------

If you have already installed Common Groups software and dependencies, and have
a PostgreSQL server running with the RDKit extension installed, then you can
use some tools included with Common Groups to automatically download data and
set up a database.

-  Clone or download the Common Groups `repository`_.

-  First, download the data::

      bash tools/download_epa.sh <source_data_dir>

   Where ``<source_data_dir>`` is a directory where you want to store EPA data
   files (*not* the PostgreSQL data directory). If you do not have the ``bash``
   shell on your system (i.e., Windows), it's probably easier to just download
   using the links above.

-  Process the data to create a structure-searchable database::

      python tools/construct_database.py -u <db_url> -d <source_data_dir>

   Where ``<db_url>`` is the database URL and ``<source_data_dir>`` is the same
   directory where EPA data was downloaded. **Note: This will take a long time
   and consume significant computational resources!**


Next steps
----------

After installing, :ref:`configure <config>` Common Groups on your system to
use the proper database, preferred file locations, and a :ref:`Google
Service Account <googlesetup>` (optional).

.. _Python: https://www.python.org/
.. _Anaconda: https://www.continuum.io/
.. _Miniconda: https://conda.io/miniconda.html
.. _conda: https://conda.io/docs/
.. _PostgreSQL: https://www.postgresql.org/
.. _RDKit/PostgreSQL:
   https://github.com/rdkit/rdkit/blob/master/Docs/Book/Install.md
.. _repository: https://github.com/akokai/commongroups
