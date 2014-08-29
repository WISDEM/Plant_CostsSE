.. _documentation-label:

.. currentmodule:: nrel_csm_bos.nrel.csm.bos

Documentation
-------------

Documentation for NREL_CSM_BOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_BOS:

.. literalinclude:: ../src/nrel_csm_bos/nrel_csm_bos.py
    :language: python
    :start-after: bos_csm_assembly(ExtendedBOSCostModel)
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



.. currentmodule:: nrel_csm_om.nrel.csm.om

Documentation for NREL_CSM_OM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OM:

.. literalinclude:: ../src/nrel_csm_om/nrel_csm_om.py
    :language: python
    :start-after: om_csm_assembly(ExtendedOPEXModel)
    :end-before: def configure(self)
    :prepend: class om_csm_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: nrel_csm_om.nrel_csm_om
.. class:: om_csm_component
.. class:: om_csm_assembly

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI


.. currentmodule:: ecn_offshore_om.ecn_offshore_om

Documentation for ECN_Offshore_OM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OM:

.. literalinclude:: ../src/ecn_offshore_om/ecn_offshore_om.py
    :language: python
    :start-after: om_ecn_assembly(ExtendedOPEXModel)
    :end-before: def __init__(self, ssfile)
    :prepend: class om_ecn_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: ecn_offshore_om.ecn_offshore_om
.. class:: om_ecn_offshore_component
.. class:: om_ecn_assembly

Supporting Models Including Excel Wrapper
==========================================
.. module:: ecn_offshore_om.ecnomXLS
.. class:: ecnomXLS

.. module:: xcel_wrapper
.. class:: Excel_Wrapper
