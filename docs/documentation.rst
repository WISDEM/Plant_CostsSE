.. _documentation-label:

.. currentmodule:: plant_costsse.nrel_csm_bos.nrel.csm.bos

Documentation
-------------

Documentation for NREL_CSM_BOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_BOS:

.. literalinclude:: ../src/plant_costsse/nrel_csm_bos/nrel_csm_bos.py
    :language: python
    :start-after: bos_csm_assembly(Assembly)
    :end-before: def configure(self)
    :prepend: class bos_csm_assembly(Assembly):

Referenced Balance of Station Cost Modules
===========================================
.. module:: plant_costsse.nrel_csm_bos.nrel_csm_bos
.. class:: bos_csm_component
.. class:: bos_csm_assembly

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI



.. currentmodule:: plant_costsse.nrel_csm_opex.nrel_csm_opex

Documentation for NREL_CSM_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OPEX:

.. literalinclude:: ../src/plant_costsse/nrel_csm_opex/nrel_csm_opex.py
    :language: python
    :start-after: opex_csm_assembly(Assembly)
    :end-before: def configure(self)
    :prepend: class opex_csm_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: plant_costsse.nrel_csm_opex.nrel_csm_opex
.. class:: opex_csm_component
.. class:: opex_csm_assembly

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI

.. currentmodule:: plant_costsse.nrel_land_bosse.nrel_land_bosse

Documentation for NREL_Land_BOSSE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following inputs and outputs are defined for NREL_Land_BOSSE:

.. literalinclude:: ../src/plant_costsse/nrel_land_bosse/nrel_land_bosse.py
    :language: python
    :start-after: NREL_Land_BOSSE(Assembly)
    :end-before: def __init__(self, ssfile=None)
    :prepend: class NREL_Land_BOSSE(Assembly):

Referenced Land BOS Modules
===========================================
.. module:: plant_costsse.nrel_land_bosse.nrel_land_bosse
.. class:: Enum2Int
.. class:: FarmSize
.. class:: Defaults
.. class:: Transportation
.. class:: Engineering
.. class:: PowerPerformance
.. class:: AccessRoads
.. class:: SiteCompound
.. class:: Building
.. class:: Foundations
.. class:: Erection
.. class:: ElecMaterials
.. class:: ElecInstallation
.. class:: Substation
.. class:: Transmission
.. class:: ProjectMgmt
.. class:: Development
.. class:: Insurance
.. class:: Markup
.. class:: Total


.. currentmodule:: plant_costsse.ecn_offshore_opex.ecn_offshore_opex

Documentation for ECN_Offshore_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following inputs and outputs are defined for NREL_CSM_OPEX:

.. literalinclude:: ../src/plant_costsse/ecn_offshore_opex/ecn_offshore_opex.py
    :language: python
    :start-after: opex_ecn_assembly(Assembly)
    :end-before: def __init__(self, ssfile=None)
    :prepend: class opex_ecn_assembly(Assembly):

Referenced Operational Expenditure Modules
===========================================
.. module:: plant_costsse.ecn_offshore_opex.ecn_offshore_opex
.. class:: opex_ecn_offshore_component
.. class:: opex_ecn_assembly

Supporting Models Including Excel Wrapper (via CommonSE)
=========================================================
.. module:: plant_costsse.ecn_offshore_opex.ecnomXLS
.. class:: ecnomXLS

.. module:: commonse.xcel_wrapper
.. class:: ExcelWrapper

Referenced PPI Index Models (via commonse.config)
=================================================
.. module:: commonse.csmPPI
.. class:: PPI