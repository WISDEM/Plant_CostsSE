Installation
------------

.. admonition:: prerequisites
   :class: warning

	General: NumPy, SciPy, Swig, pyWin32, MatlPlotLib, Lxml, OpenMDAO

	Wind Plant Framework: FUSED-Wind (Framework for Unified Systems Engineering and Design of Wind Plants)

	Sub-Models: CommonSE

	Supporting python packages: Pandas, Algopy, Zope.interface, Sphinx, Xlrd, PyOpt, py2exe, Pyzmq, Sphinxcontrib-bibtex, Sphinxcontrib-zopeext, Numpydoc, Ipython

Clone the repository at `<https://github.com/WISDEM/Plant_CostsSE>`_
or download the releases and uncompress/unpack (Plant_CostsSE.py-|release|.tar.gz or Plant_CostsSE.py-|release|.zip) from the website link at the bottom the `Plant_CostsSE site<http://nwtc.nrel.gov/Plant_CostsSE>`_.

To install Plant_CostsSE, first activate the OpenMDAO environment and then install with the following command.

.. code-block:: bash

   $ plugin install

To check if installation was successful try to import the module from within an activated OpenMDAO environment:

.. code-block:: bash

    $ python

.. code-block:: python

	> import plant_costsse.nrel_csm_bos.nrel_csm_bos
	> import plant_costsse.nrel_csm_opex.nrel_csm_opex
	> import plant_costsse.ecn_opex_offshore.ecn_opex_offshore

Note that you must have the ECN Offshore OPEX model and license in order to use the latter module.  This software contains only the OpenMDAO wrapper for the model.

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

.. code-block:: bash

   $ python src/test/test_Plant_CostsSE.py

An "OK" signifies that all the tests passed.

If you have the ECN model, you may run the ECN test which checks for a non-zero value for operational expenditures.  You will likely need to modify the code for the ECN model based on the version you have and its particular configuration.

.. code-block:: bash

   $ python src/test/test_Plant_CostsSE_ECN.py

For software issues please use `<https://github.com/WISDEM/Plant_CostsSE/issues>`_.  For functionality and theory related questions and comments please use the NWTC forum for `Systems Engineering Software Questions <https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002>`_.

.. only:: latex

    An HTML version of this documentation that contains further details and links to the source code is available at `<http://wisdem.github.io/Plant_CostsSE>`_

