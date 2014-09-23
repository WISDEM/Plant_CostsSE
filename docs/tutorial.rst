.. _tutorial-label:

.. currentmodule:: plant_costsse.docs.examples.example


Tutorial
--------

Tutorial for NREL_CSM_BOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example of NREL_CSM_BOS, let us simulate balance of station costs for a land-based wind plant.

The first step is to import the relevant files and set up the component.

.. literalinclude:: examples/example.py
    :start-after: # 1 ---
    :end-before: # 1 ---

The plant balance of station cost model relies on some turbine as well as plant input parameters that must be specified.  In this case, the wind turbine machine rating, rotor diameter, overall cost, and hub height need to be specified.  The rotor-nacelle-assembly (RNA) mass is also included but is not used in the model at this time.  For plant inputs, the number of turbines, sea depth, analysis year and month need to be specified.  A multiplier input is available if there is a desire to calibrate the model to some known wind plant costs.

.. literalinclude:: examples/example.py
    :start-after: # 2 ---
    :end-before: # 2 ---

We can now evaluate the plant balance of station costs.

.. literalinclude:: examples/example.py
    :start-after: # 3 ---
    :end-before: # 3 ---

We then print out the resulting cost values.

.. literalinclude:: examples/example.py
    :start-after: # 4 ---
    :end-before: # 4 ---

The result is:

>>> Balance of Station Costs for an offshore wind plant with 100 NREL 5 MW turbines
>>> BOS cost offshore: $766464743.61 USD
>>> BOS cost per turbine: $7664647.44 USD

Next we repeat the process but change the input settings for an land-based wind plant.

.. literalinclude:: examples/example.py
    :start-after: # 5 ---
    :end-before: # 5 ---

The new result is:

>>> Balance of Station Costs for an land-based wind plant with 100 NREL 5 MW turbines
>>> BOS cost onshore: $308453311.95 USD
>>> BOS cost per turbine: $3084533.12 USD


Tutorial for NREL_CSM_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example of NREL_CSM_OPEX, let us simulate operational expenditures for a land-based wind plant.  

The first step is to import the relevant files and set up the component.

.. literalinclude:: examples/example.py
    :start-after: # 6 ---
    :end-before: # 6 ---

The plant operational expenditures model relies on some turbine as well as plant input parameters that must be specified.  For the OPEX model, the turbine machine rating must be specified as well as plant parameters including the net annual energy production of the plant, the number of turbines and the sea depth.  The analysis year and month must also be specified.

.. literalinclude:: examples/example.py
    :start-after: # 7 ---
    :end-before: # 7 ---

We can now evaluate the plant operational expenditures.

.. literalinclude:: examples/example.py
    :start-after: # 8 ---
    :end-before: # 8 ---

We then print out the resulting cost values.

.. literalinclude:: examples/example.py
    :start-after: # 9 ---
    :end-before: # 9 ---

The result is:

>>> Average annual operational expenditures for an offshore wind plant with 100 NREL 5 MW turbines
>>> OPEX offshore: $47575391.88 USD
>>> Preventative OPEX by turbine: $364542.00 USD
>>> Corrective OPEX by turbine: $91048.39 USD
>>> Land Lease OPEX by turbine: $20163.53 USD

Next we repeat the process but change the input settings for an land-based wind plant.

.. literalinclude:: examples/example.py
    :start-after: # 10 ---
    :end-before: # 10 ---

The new result is:

>>> Average annual operational expenditures for an land-based wind plant with 100 NREL 5 MW turbines
>>> OPEX land-based: $20955230.02 USD
>>> Preventative OPEX by turbine: $130689.55 USD
>>> Corrective OPEX by turbine: $58699.22 USD
>>> Land Lease OPEX by turbine: $20163.53 USD

Tutorial for ECN_Offshore_OPEX
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example of ECN_Offshore_OPEX, let us simulate operational expenditures for an offshore wind plant.  

The first step is to import the relevant files and set up the component.  Note that the location of the ECN model must be specified as an input to the wrapper.

.. literalinclude:: examples/example.py
    :start-after: # 11 ---
    :end-before: # 11 ---

The plant operational expenditures model relies on some turbine as well as plant input parameters that must be specified.  At the moment these include the turbine machine rating and overall cost as well as the number of turbines in the plant and the expected project lifetime.

.. literalinclude:: examples/example.py
    :start-after: # 12 ---
    :end-before: # 12 ---

We can now evaluate the plant operational expenditures.

.. literalinclude:: examples/example.py
    :start-after: # 13 ---
    :end-before: # 13 ---

We then print out the resulting cost values.

.. literalinclude:: examples/example.py
    :start-after: # 14 ---
    :end-before: # 14 ---

The results will vary depending on the configuration of the model but example results are provided here:

>>> Average annual operational expenditures for an offshore wind plant with 100 NREL 5 MW turbines
>>> OPEX offshore: $60080182.54 USD
>>> Preventative OPEX by turbine: $56525.74 USD
>>> Corrective OPEX by turbine: $389276.09 USD
>>> Land Lease OPEX by turbine: $105000.00 USD
>>> and plant availability of 94.3%



