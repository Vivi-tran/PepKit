.. _getting-started-pepkit:

Getting Started
===============

Welcome to the **PepKit** documentation! This guide walks you through installing and verifying **PepKit**, a toolkit for peptide modeling, analysis, and peptide-centric informatics workflows.

Introduction
------------
**PepKit** provides a suite of tools for peptide sequence parsing, format conversion (FASTA/SMILES), descriptor calculation, clustering, structural modeling, and docking workflows. Whether you’re building machine learning models or automating peptide data pipelines, **PepKit** helps you get started quickly and scale confidently.

Requirements
------------
Before installing **PepKit**, ensure that:

- **Python** ≥ 3.11 is available on your system.
- (Recommended) You use an isolated virtual environment to avoid dependency conflicts.
- Some features may require external tools (see below).

Virtual Environment (Recommended)
---------------------------------
Creating an isolated environment prevents conflicts between **PepKit** and other Python projects.

1. **Using venv** (cross-platform):

   .. code-block:: bash

      python3 -m venv pepkit-env
      source pepkit-env/bin/activate    # Linux/macOS
      pepkit-env\Scripts\activate       # Windows PowerShell

2. **Using Conda** (if you prefer Conda environments):

   .. code-block:: bash

      conda create -n pepkit-env python=3.11
      conda activate pepkit-env

Installing Dependencies
-----------------------
All core features require only standard Python packages. If your workflow uses 3D structure modeling or docking, you may need to install external tools (e.g., RDKit, AlphaFold, Rosetta) as described in the advanced documentation.

Installing PepKit
-----------------
With your environment activated, install **PepKit** from PyPI:

   .. code-block:: bash

      pip install pepkit

Or install the latest development version from GitHub:

   .. code-block:: bash

      git clone https://github.com/Vivi-tran/PepKit.git
      cd PepKit
      pip install -e .

This will pull in **PepKit** and all required dependencies.

Quick Verification
------------------
After installation, verify that **PepKit** is available and check its version:

   .. code-block:: bash

      python -c "import pepkit; print(pepkit.__version__)"
      # Should print the installed pepkit version

Further Resources
-----------------
- Tutorials and examples: `See the examples.ipynb <https://github.com/Vivi-tran/PepKit/blob/main/examples/examples.ipynb>`_


Support
-------
If you encounter issues or have questions:
- Report bugs and feature requests on GitHub: `PepKit Issues <https://github.com/Vivi-tran/PepKit/issues>`_

Enjoy using **PepKit**!
