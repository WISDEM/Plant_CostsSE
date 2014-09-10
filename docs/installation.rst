Installation
------------

.. admonition:: prerequisites
   :class: warning

   NumPy, SciPy, FUSED-Wind, OpenMDAO

Clone the repository at `<https://github.com/WISDEM/Plant_CostsSE>`_
or download the releases and uncompress/unpack (Plant_CostsSE.py-|release|.tar.gz or Plant_CostsSE.py-|release|.zip)

To install Plant_CostsSE, first activate the OpenMDAO environment and then install with the following command.

.. code-block:: bash

   $ plugin install

To check if installation was successful try to import the module

.. code-block:: bash

    $ python

.. code-block:: python

    > import nrel_csm_bos.nrel_csm_bos
    > import nrel_csm_opex.nrel_csm_opex
    > import ecn_opex_offshore.ecn_opex_offshore

Note that you must have the ECN Offshore OPEX model and license in order to use the latter module.  This software contains only the OpenMDAO wrapper for the model.

You can also run the unit tests for the gradient checks

.. code-block:: bash

   $ python src/test/test_Plant_CostsSE_gradients.py

An "OK" signifies that all the tests passed.

.. only:: latex

    An HTML version of this documentation that contains further details and links to the source code is available at `<http://wisdem.github.io/Plant_CostsSE>`_

