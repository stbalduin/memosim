# MeMoSim
This repository is part of the MeMoBuilder. MeMoBuilder is a Python toolbox which can be used to build surrogate models. This module provides a simple simulation environment structure which is used by MeMoBuilder and MeMoDb.
# Acknowledgement
Parts of this software have been developed by OFFIS - Institute for Information Technology. We would like to thank both the board and the research division Energy for the possibility to publish this software under the MIT license.

# About MeMoSim
Installation Instructions (Linux)
---------------------------------

1. Create a virtual environment:

    `$ virtualenv -p /usr/bin/python3 ~/.virtualenvs/memobuilder`

2. Activate the virtual environment:

    `$ source ~/.virtualenvs/memobuilder/bin/activate`
    
    `(memobuilder)$ ...`

3. Install the requirements

    `(memobuilder)$ pip install cython numpy`

4. Install MeMoSim
  
    `(memobuilder)$ pip install git+git://github.com/stbalduin/memosim`

Building the documentation
--------------------------

The documentation is built using `Sphinx <http://sphinx-doc.org>`_ and
`PlantUML <http://plantuml.com/>`_. `PlantUML.jar <http://plantuml.com/>`_ is included in the ``docs`` folder.
Other requirements are
`Sphinx RTD Theme <https://pypi.python.org/pypi/sphinx_rtd_theme>`_ and
`sphinxcontrib-plantuml <https://pypi.python.org/pypi/sphinxcontrib-plantuml>`_.

Requirements:

* `Sphinx <http://sphinx-doc.org>`_ >= 1

* `Sphinx RTD Theme <https://pypi.python.org/pypi/sphinx_rtd_theme>`_ >= 0.1.9

* `sphinxcontrib-plantuml  <https://pypi.python.org/pypi/sphinxcontrib-plantuml>`_ >= 0.8.1

The following command builds the documentation if called from within the
``docs`` directory::

    $ make html
