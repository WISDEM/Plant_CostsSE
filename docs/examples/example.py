# 1 ---------

# A simple test of nrel_csm_bos model
from plant_costsse.nrel_csm_bos.nrel_csm_bos import bos_csm_assembly

bos = bos_csm_assembly()

# 1 ---------
# 2 ---------

# Set input parameters
bos = bos_csm_assembly()
bos.machine_rating = 5000.0
bos.rotor_diameter = 126.0
bos.turbine_cost = 5950209.28
bos.hub_height = 90.0
bos.RNA_mass = 256634.5 # RNA mass is not used in this simple model
bos.turbine_number = 100
bos.sea_depth = 20.0
bos.year = 2009
bos.month = 12
bos.multiplier = 1.0

# 2 ---------
# 3 ---------

bos.run()

# 3 ---------
# 4 --------- 

print "Balance of Station Costs for an offshore wind plant with 100 NREL 5 MW turbines"
print "BOS cost offshore: ${0:.2f} USD".format(bos.bos_costs)
print "BOS cost per turbine: ${0:.2f} USD".format(bos.bos_costs / bos.turbine_number)
print

# 4 ----------
# 5 ----------

bos.sea_depth = 0.0
bos.turbine_cost = 5229222.77

bos.run()

print "Balance of Station Costs for an land-based wind plant with 100 NREL 5 MW turbines"
print "BOS cost land-based: ${0:.2f} USD".format(bos.bos_costs)
print "BOS cost per turbine: ${0:.2f} USD".format(bos.bos_costs / bos.turbine_number)
print

# 5 ---------- 
# 6 ----------

# A simple test of nrel_csm_om model
from plant_costsse.nrel_csm_opex.nrel_csm_opex import opex_csm_assembly

om = opex_csm_assembly()

# 6 ----------
# 7 ----------

# Ste input parameters
om.machine_rating = 5000.0 # Need to manipulate input or underlying component will not execute
om.net_aep = 1701626526.28
om.sea_depth = 20.0
om.year = 2009
om.month = 12
om.turbine_number = 100

# 7 ----------
# 8 ----------

om.run()

# 8 -----------
# 9 -----------

print "Average annual operational expenditures for an offshore wind plant with 100 NREL 5 MW turbines"
print "OPEX offshore ${:.2f}: USD".format(om.avg_annual_opex)
print "Preventative OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.preventative_opex / om.turbine_number)
print "Corrective OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.corrective_opex / om.turbine_number)
print "Land Lease OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.lease_opex / om.turbine_number)
print

# 9 -----------
# 10 -----------

om.sea_depth = 0.0
om.run()
print "Average annual operational expenditures for an land-based wind plant with 100 NREL 5 MW turbines"
print "OPEX land-based: ${:.2f} USD".format(om.avg_annual_opex)
print "Preventative OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.preventative_opex / om.turbine_number)
print "Corrective OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.corrective_opex / om.turbine_number)
print "Land Lease OPEX by turbine: ${:.2f} USD".format(om.opex_breakdown.lease_opex / om.turbine_number)
print

# 10 -----------
# 11 ----------

# A simple test of ecn_offshore_om model
from plant_costsse.ecn_offshore_opex.ecn_offshore_opex import opex_ecn_assembly

om2 = opex_ecn_assembly('C:/Models/ECN Model/ECN O&M Model.xls') # Substitute your own path to the ECN Model

# 11 ----------
# 12 ----------

# Set input parameters
om2.machine_rating = 5000.0
om2.turbine_cost = 9000000.0
om2.turbine_number = 100
om2.project_lifetime = 20

# 12 ----------
# 13 ----------

om2.run()

# 13 ----------
# 14 ----------

print "Average annual operational expenditures for an offshore wind plant with 100 NREL 5 MW turbines"
print "OPEX offshore: ${:.2f} USD".format(om2.avg_annual_opex)
print "Preventative OPEX by turbine: ${:.2f} USD".format(om2.opex_breakdown.preventative_opex / om2.turbine_number)
print "Corrective OPEX by turbine: ${:.2f} USD".format(om2.opex_breakdown.corrective_opex / om2.turbine_number)
print "Land Lease OPEX by turbine: ${:.2f} USD".format(om2.opex_breakdown.lease_opex / om2.turbine_number)
print "and plant availability of {:.1f}% ".format(om2.availability*100.0)
print

# 14 ----------