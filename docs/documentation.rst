.. _documentation-label:

.. currentmodule:: nrel_csm_bos.nrel.csm.bos

Documentation
-------------

Documentation for NREL_CSM_BOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_BOS:

.. literalinclude:: ../src/nrel_csm_bos/nrel_csm_bos.py
    :language: python
    :start-after: bos_csm_assembly(Assembly)
    :end-before: def configure(self)
    :prepend: class bos_csm_assembly(Assembly):

Referenced Balance of Station Cost Modules
===========================================
.. module:: nrel_csm_bos.nrel_csm_bos
.. class:: bos_csm_component
.. class:: bos_csm_assembly

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI



.. currentmodule:: nrel_csm_opex.nrel_csm_opex

Documentation for NREL_CSM_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OPEX:

.. literalinclude:: ../src/nrel_csm_opex/nrel_csm_opex.py
    :language: python
    :start-after: opex_csm_assembly(Assembly)
    :end-before: def configure(self)
    :prepend: class opex_csm_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: nrel_csm_opex.nrel_csm_opex
.. class:: opex_csm_component
.. class:: opex_csm_assembly

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI


.. currentmodule:: ecn_offshore_opex.ecn_offshore_opex

Documentation for ECN_Offshore_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OPEX:

.. literalinclude:: ../src/ecn_offshore_opex/ecn_offshore_opex.py
    :language: python
    :start-after: opex_ecn_assembly(Assembly)
    :end-before: def __init__(self, ssfile=None)
    :prepend: class opex_ecn_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: ecn_offshore_opex.ecn_offshore_opex
.. class:: opex_ecn_offshore_component
.. class:: opex_ecn_assembly

Supporting Models Including Excel Wrapper
==========================================
.. module:: ecn_offshore_opex.ecnomXLS
.. class:: ecnomXLS

.. module:: xcel_wrapper
.. class:: Excel_Wrapper
