=================
API Reference
=================

PepKit is organized into several core modules, each providing specialized functionality for peptide informatics, modeling, docking, and data handling. Browse below for detailed API documentation.

Chem Module
===========

Parser (`pepkit.chem._parser`)
------------------------------
Tools for parsing peptide representations (FASTA/SMILES), standardizing sequences, and filtering non-canonical FASTA records.

.. automodule:: pepkit.chem._parser
   :members:
   :undoc-members:
   :show-inheritance:

Property (`pepkit.chem._property`)
----------------------------------
Functions for calculating molecular and sequence-based properties for peptides.

.. automodule:: pepkit.chem._property
   :members:
   :undoc-members:
   :show-inheritance:

Descriptor (`pepkit.chem.descriptor`)
-------------------------------------
Calculation of molecular descriptors and physicochemical properties.

.. automodule:: pepkit.chem.descriptor
   :members:
   :undoc-members:
   :show-inheritance:

Standardize (`pepkit.chem.standardize`)
---------------------------------------
Utilities for standardizing peptide sequences and molecular representations.

.. automodule:: pepkit.chem.standardize
   :members:
   :undoc-members:
   :show-inheritance:


Metrics Module
==============

Regression Metrics (`pepkit.metrics._regression`)
-------------------------------------------------
Metrics for regression tasks such as binding affinity prediction.

.. automodule:: pepkit.metrics._regression
   :members:
   :undoc-members:
   :show-inheritance:

Classification Metrics (`pepkit.metrics._classification`)
--------------------------------------------------------
Metrics for classification tasks relevant to peptide modeling.

.. automodule:: pepkit.metrics._classification
   :members:
   :undoc-members:
   :show-inheritance:

Base Metrics (`pepkit.metrics._base`)
-------------------------------------
Core metric computation routines shared across regression and classification.

.. automodule:: pepkit.metrics._base
   :members:
   :undoc-members:
   :show-inheritance:

Common Metrics (`pepkit.metrics._common`)
-----------------------------------------
Utility functions and common scoring routines.

.. automodule:: pepkit.metrics._common
   :members:
   :undoc-members:
   :show-inheritance:

Dock Module
===========

Rosetta Refinement Dock (`pepkit.dock.rosetta.refinement_dock`)
--------------------------------------------------------------
Implements Rosetta-based peptide docking protocols.

.. automodule:: pepkit.dock.rosetta.refinement_dock
   :members:
   :undoc-members:
   :show-inheritance:

Rosetta Score (`pepkit.dock.rosetta.score`)
-------------------------------------------
Extraction and processing of Rosetta docking scores.

.. automodule:: pepkit.dock.rosetta.score
   :members:
   :undoc-members:
   :show-inheritance:

MD Module
=========

Construction of interaction fingerprint and frequency
----------------------------------------------------

.. automodule:: pepkit.md.interaction
   :members:
   :undoc-members:
   :show-inheritance:

Stability evaluation of trajectories
------------------------------------

.. automodule:: pepkit.md.stable
   :members:
   :undoc-members:
   :show-inheritance:

IO Module
=========

File IO (`pepkit.io.files`)
---------------------------
Tools for handling peptide file input/output operations.

.. automodule:: pepkit.io.files
   :members:
   :undoc-members:
   :show-inheritance:

Logging (`pepkit.io.logging`)
-----------------------------
Unified logging interface for workflow monitoring and reproducibility.

.. automodule:: pepkit.io.logging
   :members:
   :undoc-members:
   :show-inheritance:
