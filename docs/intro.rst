Introduction
------------

The set of models contained in this Plant_CostsSE are used to assess the balance of station costs and operational expenditures for a wind plant.  The first two models are based on the NREL Cost and Scaling Model :cite:`Fingersh2006` and estimate balance of station costs (NREL_CSM_BOS) and operational expenditures (NREL_CSM_OPEX) for both land-based and offshore wind plants.  The latter software is a wrapper for an offshore operational expenditures model from the Energy Research Centre of the Netherlands (ECN) :cite:`ECN2012` and one must have the model and license in order to use this model.  Only an OpenMDAO wrapper for the model is provided in this software set.

Plant_CostsSE is implemented as an `OpenMDAO <http://openmdao.org/>`_ assembly.  All supporting code is also in OpenMDAO based on the Python programming language with the exception of the ECN Offshore OPEX model which is in Excel.  You must have the model and license in order to use this model.
