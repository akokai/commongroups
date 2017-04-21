Usage
=====

.. _running:

Running ``commongroups``
------------------------

Once the package is installed, the program can be run from the command line
using::

   commongroups [options]

Use the option ``--help`` to get a list of all the available options.

If the program runs successfully, it will output numerous files in the
``results`` subdirectory of whatever project environment you are using. The best
way to view results is to open the ``results/html/index.html`` file in your
browser. This will contain links to all the results in your project.

Read further for an explanation of projects, environments, and configuration
options.

.. _environments:

Environments
------------

The program is designed to keep all of its data and files within a particular
directory on your system -- the "home" environment. Within that, it organizes
files into "project" environments. You can maintain multiple different projects
in which you use ``commongroups`` to work on separate collections of data,
results, etc.

-  The *home environment* contains all project directories, and can contain a
   global :ref:`configuration <config>` file.

-  You can specify the location of the home environment in a number of ways:

   -  When running the commongroups script, use the ``-e`` option::

         commongroups -e /path/to/commongroups_home [options...]

   -  Set an an environment variable ``CMG_HOME``, for example, by adding this
      line to your shell configuration::

         $ export CMG_HOME=/path/to/commongroups_home

   -  If you don't specify anything, the defaults location is
      ``<user home>/commongroups_data``.

-  *Project environments* are subdirectories of the home environment.
   The name of each project is the name of the directory
   where its data are stored. You can have any number of projects.

   -  Projects directories will be automatically created, and will
      contain ``data``, ``log``, and ``results`` subdirectories.

   -  You can specify a project when you run Common Groups, using the ``-p``
      option::

         commongroups -p <project_name> [options...]

   -  If you don't specify a project, your data will go in
      ``<commongroups home>/default``.


.. _config:

Configuration
-------------

Rather than *always* having to give many command-line options, such as your
system's database URL and the location of your Google key file, it's easier to
**create a configuration file** to store all this information. If the home
environment contains a file called ``config.json``, then this file will be read
every time Common Groups is run.

The format of the configuration file must be valid JSON. The example code below
is included in ``tools`` directory of the repository. You can specify any of the
following options::

   {
     "database_url": "postgresql://user@localhost/cmgdata",
     "google_key_file": "/path/to/google-credentials-keyfile.json",
     "google_sheet_title": "Compound group parameters",
     "google_worksheet": "active"
   }

.. _googlesetup:

Google Sheets access
--------------------

If you want to access a Google Sheet that contains compound group parameters,
you must have Google Service Account credentials. Steps to obtain this:

-  Create `Google API`_ credentials for accessing Google Drive. This requires a
   Google account. See the `gspread docs`_ for more detailed instructions.

-  Download a **key file** (JSON format) containing your Google service account
   credentials and save it somewhere secure.

-  Create, or otherwise gain access to, a Google Spreadsheet in which the
   compound group parameters will be specified.

-  Share the relevant Google Sheet with your Google service account client
   e-mail address (it's in the key file).

To enable ``commongroups`` to access your spreadsheet, specify the following
information either as command-line options or in your configuration file:

-  The path to your key file (``-k``)

-  The title of the *document* (``-g``) and of the specific *worksheet*, e.g.,
   "Sheet1" (``-w``) that contains group parameters.

Reading parameters from a file
------------------------------

Instead of getting parameters from a Google Sheet, it's possible to read them
from a file. Specify the file path using the ``-f`` option::

   commongroups -f <file> [options...]

Currently, the only file format supported is JSON. The `testing parameter set`_
can serve as an example of the format.

.. _gspread docs: http://gspread.readthedocs.io/en/latest/oauth2.html
.. _Google API:
   https://console.developers.google.com/projectselector/apis/credentials
.. _testing parameter set:
   https://github.com/akokai/commongroups/blob/master/commongroups/tests/params.json
