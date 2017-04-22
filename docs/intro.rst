Introduction
============

**Common Groups** is a project for molecular structure-based classification of
chemical substances into groups with known environmental health hazards. This is
part of a broader effort to develop information infrastructure for chemical
hazard assessment and alternatives assessment.

This documentation is specifically about ``commongroups``, a software package
written in Python. It provides computational methods to identify sets of
chemicals belonging to structurally-defined classes.

Purpose
-------

Certain *groups* or *classes* of chemical substances are of interest for their
environmental or toxicological hazard characteristics. Chemical `hazard
screening methods`_ and regulatory agencies reference several hundred such
groups. However, determining the actual set of substances that might belong to
each group is usually left up to someone else.

The Common Groups project aims to address this gap though the collaborative
development of molecular structure-based "definitions" for chemical groups of
interest, supported by software tools and shared information resources. The
collaborative effort will be convened and documented by the `Chemical Hazard
Data Commons`_.

The goal of the Common Groups software tool is to apply basic cheminformatics
techniques to:

-  Find all substances within a larger set that belong to a given group.

-  Classify individual substances into the correct group(s).

-  Perform these functions automatically for a large number of groups all at
   once.

We imagine the possible applications of this project to include answering
questions such as: *What dithiocarbamates are in this list of compounds?* or
*Does this new compound belong to any chemical groups associated with endocrine
disruption?*


Frequently asked questions
--------------------------

**Does this program use structural similarity searching?** No, it uses
substructure matching. The idea is that the groups of chemicals we want to
identify are defined by precise criteria, rather than inferred by similarity. We
see this approach as complementary to similarity searching methods, with each
approach having different advantages.

**Is this a tool for identifying toxicophores?** No. Toxicophore identification
is part of the rational basis for defining groups of substances by structure,
and is therefore a background condition, not a function, of this project.

**Isn't this project limited by the current state of knowledge linking
individual groups of chemicals to individual hazard endpoints?** Yes. The
purpose of this project is not to create new knowledge *about* compound groups,
but to identify potentially new *associations* between specific compounds and
hazards, based on existing knowledge.

.. _hazard screening methods:
   https://www.greenscreenchemicals.org/learn/greenscreen-list-translator
.. _Chemical Hazard Data Commons: https://commons.healthymaterials.net/
