Design
======

General concepts
----------------

We understand **compound groups** to be sets of substances defined by their
shared molecular features, and which are useful to consider as a group because
they share other properties of interest.

The premise for grouping chemicals together is that many substances share
substantial similarities in toxicological characteristics. The notion that
these similarities are related to underlying similarities in molecular
structure is supported by toxicological research (Kazius et al., 2005; Singh et
al., 2016). Environmental fate and exposure potential are also known to be
related to molecular structure, making compound groups an important unit of
analysis in chemical hazard assessment and in the environmental health sciences
more broadly (Krowech et al., 2016).

Compounds groups of toxicological interest can be identified by a number of
research strategies, including computational and predictive toxicology
approaches (Faulkner et al., 2017).

Our focus, however, is on enumerating compounds that belong to groups *already
identified* through established methods. Over several decades of toxicological,
epidemiological, and regulatory science worldwide, several hundred compound
groups have been recognized and associated with known health hazards. For
example, `IARC <http://monographs.iarc.fr/>`_ classifies "Nickel compounds" and
several other compound groups according to their carcinogenicity.

See below for :ref:`references <toxrefs>`.


Methods for associating compounds with groups
---------------------------------------------

Computational tools already exist for analyzing and searching molecular
structures. Given a broad enough *set of relevant molecular structures*, and a
set of :ref:`defined <definitions>` *structural patterns* corresponding to
compound groups of interest, it should be possible to apply existing
computational methods to identify which compounds belong to which group(s). That
is the goal of Common Groups.

Thus, we sometimes describe our project as **"populating" groups** with relevant
examples of substances that belong to those groups. The immediate intended
application of this project is to give technical definitions and enable
computationally populating the set of compound groups named throughout all the
hazard identification sources of the `GreenScreen for Safer Chemicals`_ and the
`GreenScreen List Translator`_.


Design of this program
----------------------

The ``commongroups`` software automates the process of going from a compound
group definition to a list of substances that belong to the group. The program
reads technical definitions of compound groups from a Google Spreadsheet. In
the spreadsheet, the users of the program must define each group using the set
of :ref:`parameters <parameters>` described below. With these definitions, the
program searches a database of molecular structures looking for matches to the
patterns; hundreds of thousands of compounds can be evaluated automatically in
this way.  Finally, the program generates lists of matching compounds, and
reports its results in the form of a web-browseable directory of groups.

To describe the "search" process in slightly more technical terms: For each
compound group, ``commongroups`` formulates a database query that expresses the
specified structural patterns and selection logic. It then runs this query
against a local database of chemical structures, and retrieves the resulting set
of compounds that match the group definition. Essential to this processs is the
`RDKit`_ open-source cheminformatics toolkit, which enables database querying
using molecular structure comparisons.

The actual compounds identified when a group is populated using ``commongroups``
will necessarily depend on what compounds are represented in the database that
is used. For information about how we construct a database for this purpose, see
:doc:`database`. For detailed technical documentation about how the
program works, see :doc:`usage` and the :doc:`developer`.

.. _definitions:

Defining groups
---------------

In this project we define groups by specifying one or more patterns in molecular
structure. We express these patterns in `SMARTS`_ notation (or, if very simple,
sometimes in `SMILES`_ notation). For some groups, we may need to specify
multiple patterns linked by logical conditions ("and", "or", "not", etc.). Here
are a few simple examples of molecular patterns that correpsond to compound
groups of toxicological interest.

========================   ============================
Compound group             Structure pattern (SMARTS)
========================   ============================
Mercury compounds, alkyl   ``[Hg]C``
Diazonium salts            ``[C,c][N+]#[N]``
Methacrylates              ``[CH3]C(=[CH2])C(=O)O-[*]``
========================   ============================

Since SMARTS expressions are not very intuitive or easily understood, it is
helpful to be able to visualise the meaning of a SMARTS expression. To that end,
we recommend a useful web app called `SMARTSviewer`_ developed at the University
of Hamburg.

We believe that the technical definitions of compound groups should be openly
discussed and peer-reviewed to ensure their accuracy and robustness. This aspect
of the Common Groups project will be documented and conducted elsewhere.

.. _parameters:

Parameters for defining a compound group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following parameters define a compound group. However, note that this is
subject to change as the project and software develops.

-  ``cmg_id``: A unique identifier for the group.

-  ``name``: The name of the group, e.g., "Phthalates".

-  ``method``: The search method for identifying compounds in the group. We
   anticipate possibly having a range of computational methods available, but
   in the current (early) version of this software, the only option is ``SQL``.

-  ``structure_type``: How the structure is notated, i.e., SMILES or SMARTS.

-  ``structure``: The structure or pattern used as input to the search method.

-  ``code``: The criteria for how compounds should be evaluated to determine
   whether or not they match the structural pattern. For the time being, these
   definitions must be written in `SQL`_, a programming language used in
   database operations.

   -  Specifically, this parameter corresponds to the ``where`` clause of a SQL
      ``select`` statement.

   -  The substrings ``:m`` and ``:s`` will be substituted with the name of the
      database column containing molecular structures, and the value of the
      ``structure`` parameter, respectively.

Examples
^^^^^^^^

Here is an example of some group parameters in tabular form, as they would
appear in a spreadsheet:

====== ======================== ========= ============== ========= =============
cmg_id name                     method    structure_type structure code
====== ======================== ========= ============== ========= =============
1001   Lead compouds            SQL       SMILES         ``[Pb]``  ``:m @> :s``
2002   Mercury compounds, alkyl SQL       SMARTS         ``[Hg]C`` ``:m @> :s ::qmol``
====== ======================== ========= ============== ========= =============

In this example, note that lead compounds are defined with a very simple SMILES
string, which just specifies the element lead. The query code expresses a
substructure search: any molecule containing the lead atom as a substructure is
matched. In contrast, alkyl mercury compoounds requires a slightly more nuanced
definition, and we use SMARTS to specify the pattern of a mercury atom bound to
a *non-aromatic* carbon. We also include the ``::qmol`` term in the query code
to indicate that the structure is a query molecule.

In addition to these technical parameters, compound groups can be further
described by adding notes or plain-language descriptions. This information is
not used for computational purposes, but can be included for interpretation and
communication of results. In the ``commongroups`` spreadsheet format, any
columns *after* the parameters are read in as additional information.

In the next section, we describe the form of database that is necessary to
perform compound group population using these kinds of definitions.

.. _toxrefs:

References
----------

-  Kazius, J., McGuire, R., & Bursi, R. (2005). Derivation and validation of
   toxicophores for mutagenicity prediction. *Journal of Medicinal Chemistry*,
   48(1), 312–320. https://doi.org/10.1021/jm040835a

-  Singh, P. K., Negi, A., Gupta, P. K., Chauhan, M., & Kumar, R. (2016).
   Toxicophore exploration as a screening technology for drug design and
   discovery: Techniques, scope and limitations. *Archives of Toxicology*,
   90(8), 1785–1802. https://doi.org/10.1007/s00204-015-1587-5

-  Krowech, G., Hoover, S., Plummer, L., Sandy, M., Zeise, L., & Solomon, G.
   (2016). Identifying chemical groups for biomonitoring. *Environmental Health
   Perspectives,* 124(12), A219–A226. https://doi.org/10.1289/EHP537

-  Faulkner, D., Rubin Shen, L. K., et al. (2017). Tools for green molecular
   design to reduce toxicological risk. In R. J. Richardson & D. E. Johnson
   (Eds.), *Computational systems pharmacology and toxicology* (pp. 36–59).
   Cambridge: Royal Society of Chemistry.
   https://doi.org/10.1039/9781782623731-00036

.. _GreenScreen for Safer Chemicals: https://www.greenscreenchemicals.org/
.. _GreenScreen List Translator:
   https://www.greenscreenchemicals.org/learn/greenscreen-list-translator
.. _SMARTS: http://www.daylight.com/dayhtml/doc/theory/theory.smarts.html
.. _SMILES: http://www.daylight.com/dayhtml/doc/theory/theory.smiles.html
.. _SMARTSviewer: http://smartsview.zbh.uni-hamburg.de/smartsview/view
.. _RDKit: http://rdkit.org/
.. _SQL: https://en.wikipedia.org/wiki/SQL
