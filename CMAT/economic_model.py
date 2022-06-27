"""
@author: Mamunur Rahman
"""
# created EconomicData class

from utility_functions import Stock, Revenue, flowSum, flowProduct, flowDivide, flowAndfactor, dissolveSubs, flowSubtract

import numpy as np
import time
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from tabulate import tabulate

keys = ['crt_tv', 'crt_monitor', 'lcd_tv', 'lcd_monitor', 'desktop', 'laptop', 'printer', 'small_cee', 'computer_peri']
values = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # position of the keys in the list
item = dict(zip(keys, values))
unit_factors = [1]*len(keys)



class EconomicData:
    def __init__(self, excel_file_name):

        # read data
        self.df_mat_flow = pd.read_excel(io = excel_file_name, sheet_name= 'MaterialFlow')
        self.df_cost = pd.read_excel(io = excel_file_name, sheet_name= 'Cost')
        self.df_rev = pd.read_excel(io = excel_file_name, sheet_name= 'Revenue')

        # Prepare data for window-1: material flow
        #-----------------------------------------
        # ceate a material dictionary
        self.material_dict = self.df_mat_flow.set_index('Variable').T.to_dict('list')
        
        # Prepare data for window-2: cost calculation
        #--------------------------------------------
        df_cost = self.df_cost.copy()
        
        ## create a cost dictionary
        # 1. For variables without subscripts
        df1 = df_cost[['Variable', 'overall']].dropna()  # keep the first two columns, drop the last two rows
        # ceate a dictionary
        self.cost_dict = df1.set_index('Variable').T.to_dict('list')
        
        # 2. For variables with subscripts
        df2 = df_cost[-2:].drop(columns = ['overall'])
        # ceate a dictionary
        cost2 = df2.set_index('Variable').T.to_dict('list')
        
        # 2. Combine the two dictionaries
        self.cost_dict.update(cost2)
        # when DES model output will be used as input data
        self.cost_dict['fraction_of_utility_cost_from_shop_floor_machines'] = 0.7   # 0.7 is a placeholder
  
        # Prepare data for window-3: revenue calculation
        #-----------------------------------------------
        # ceate a price dictionary
        keys = self.df_rev.Variable.values
        values = self.df_rev.overall.values
        self.price_dict = dict(zip(keys, values))
        # update the dictionary
        self.price_dict['environmental_fee_per_lb'] = self.df_rev[self.df_rev['Variable']=='environmental_fee_per_lb'].iloc[ :, 2:].values.tolist()[0]
        


class EconomicModel:
    def __init__(self, data, get_data_from_process_model = False):
        self.d = data
        self.get_data_from_process_model = get_data_from_process_model
        
        if self.get_data_from_process_model:
            self.get_data_from_DES()
        
    
    def get_data_from_DES(self):
        process_simulation_output = pd.read_csv('process_simulation_output.csv')
        #processing_cost_per_lb_without_overhead
        self.processing_cost_per_lb_without_overhead_itemwise = process_simulation_output['processing_cost_per_lb_without_overhead'].to_list()
        self.recycled_amount_item_wise = process_simulation_output['amount_lb_per_month'].to_list()
        
    
    
    def do_calculations(self):
        
        # Get data for window-1: material flow
        material_dict = self.d.material_dict
        
        # Get data for window-2: cost calculation
        cost_dict = self.d.cost_dict
        
        # Get data for window-3: revenue calculation
        price_dict = self.d.price_dict


        #============================================================================================
        # WINDOW -1: MATERIAL FLOW
        #============================================================================================
        
        perc_remarketable_items = [0,	0,	0,	0,	0.3,	0.3,	0,	0,	0]
        
        # BUSINESS PART
        #%% part 01  Inventory_in_wh_bus
        
        # inflow
        received_amount_at_wh_bus = material_dict['recycled_amount_bus']
        
        # outflow
        perc_remarketable_items_bus = perc_remarketable_items
        perc_non_marketable_items_bus = np.array(unit_factors) - np.array(perc_remarketable_items_bus)
        
        o1 = flowAndfactor(received_amount_at_wh_bus, perc_remarketable_items_bus)
        dismantling_rate_bus = [49582.6,	6235.18,	205633,	35315.4,	38309.8,	5447.91,	94448.6,	36730.2,	49987.6] #<<<<<<<<<<<<<<<<<<<<
        
        
        #outflow2 = flowAndfactor(received_amount_at_wh_bus, perc_non_marketable_items_bus)
        #o2 = np.min([dismantling_rate_bus, outflow2], axis = 0) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        o2 = flowAndfactor(received_amount_at_wh_bus, perc_non_marketable_items_bus)
        
        
        # stock
        Inventory_in_wh_bus = Stock( inflow = received_amount_at_wh_bus, initial_stock = [], outflow = [o1, o2] )
        
        sell_to_customers_bus =Inventory_in_wh_bus.outflow[0]
        dismantled_materials_bus = Inventory_in_wh_bus.outflow[1]
        
        #%% part 02  Motherboard shredder bus
        
        # inflow
        motherboard_perc = material_dict['motherboard_perc']
        
        #outflow
        Fe_perc_motherboard = material_dict['Fe_perc_motherboard']
        Al_perc_motherboard = material_dict['Al_perc_motherboard']
        remain_material_perc_motherboard =   np.array([1]*9) - np.array(Fe_perc_motherboard) - np.array(Al_perc_motherboard)
        
        
        #stock
        motherboard_shredder_bus = Stock(inflow = dismantled_materials_bus,
                                         inflow_factors = motherboard_perc,
                                         outflow_factors = [Fe_perc_motherboard, Al_perc_motherboard, remain_material_perc_motherboard])
        
        i1 = motherboard_shredder_bus.inflow
        o1 = motherboard_shredder_bus.outflow[0]
        o2 = motherboard_shredder_bus.outflow[1]
        o3 = motherboard_shredder_bus.outflow[2]
        
        Cu_perc_motherboard_shred = material_dict['Cu_perc_motherboard_shred']
        Ag_perc_motherboard_shred = material_dict['Ag_perc_motherboard_shred']
        Au_perc_motherboard_shred = material_dict['Au_perc_motherboard_shred']
        Pd_perc_motherboard_shred = material_dict['Pd_perc_motherboard_shred']
        
        Cu_amount_motherboard_shred_bus = flowAndfactor(o3, Cu_perc_motherboard_shred)
        Ag_amount_motherboard_shred_bus = flowAndfactor(o3, Ag_perc_motherboard_shred)
        Au_amount_motherboard_shred_bus = flowAndfactor(o3, Au_perc_motherboard_shred)
        Pd_amount_motherboard_shred_bus = flowAndfactor(o3, Pd_perc_motherboard_shred)
        
        sorted_Fe_motherboard_bus = o1.copy()
        sorted_Al_motherboard_bus = o2.copy()
        remaining_shredded_materials_motherboard_bus = o3.copy()
        
        #%% part 03  HDD shredder bus
        
        # inflow
        hdd_perc = material_dict['hdd_perc']
        
        #outflow
        Fe_perc_hdd = material_dict['Fe_perc_hdd']
        Al_perc_hdd = material_dict['Al_perc_hdd']
        remain_material_perc_hdd =   np.array([1]*9) - np.array(Fe_perc_hdd) - np.array(Al_perc_hdd)
        
        
        #stock
        hdd_shredder_bus = Stock(inflow = dismantled_materials_bus,
                                 inflow_factors = hdd_perc,
                                 outflow_factors = [Fe_perc_hdd, Al_perc_hdd, remain_material_perc_hdd])
        
        i1 = hdd_shredder_bus.inflow
        o1 = hdd_shredder_bus.outflow[0]
        o2 = hdd_shredder_bus.outflow[1]
        o3 = hdd_shredder_bus.outflow[2]
        
        Cu_perc_hdd_shred = material_dict['Cu_perc_hdd_shred']
        Ag_perc_hdd_shred = material_dict['Ag_perc_hdd_shred']
        Au_perc_hdd_shred = material_dict['Au_perc_hdd_shred']
        Pd_perc_hdd_shred = material_dict['Pd_perc_hdd_shred']
        
        Cu_amount_hdd_shred_bus = flowAndfactor(o3, Cu_perc_hdd_shred)
        Ag_amount_hdd_shred_bus = flowAndfactor(o3, Ag_perc_hdd_shred)
        Au_amount_hdd_shred_bus = flowAndfactor(o3, Au_perc_hdd_shred)
        Pd_amount_hdd_shred_bus = flowAndfactor(o3, Pd_perc_hdd_shred)
        
        sorted_Fe_hdd_bus = o1.copy()
        sorted_Al_hdd_bus = o2.copy()
        remaining_shredded_materials_hdd_bus = o3.copy()
        
        
        #%% part 04  Consumer shredder bus
        
        # inflow
        # cee_perc = material_dict['cee_perc']
        cee_perc = [0, 0, 0, 0, 0, 0, 0.074, 0.92, 0.96]

        
        #outflow
        Fe_perc_cee = material_dict['Fe_perc_cee']
        Al_perc_cee = material_dict['Al_perc_cee']
        remain_material_perc_cee =   np.array([1]*9) - np.array(Fe_perc_cee) - np.array(Al_perc_cee)
        
        
        #stock
        cee_shredder_bus = Stock(inflow = dismantled_materials_bus,
                                 inflow_factors = cee_perc,
                                 outflow_factors = [Fe_perc_cee, Al_perc_cee, remain_material_perc_cee])
        
        i1 = cee_shredder_bus.inflow
        o1 = cee_shredder_bus.outflow[0]
        o2 = cee_shredder_bus.outflow[1]
        o3 = cee_shredder_bus.outflow[2]
        
        Cu_perc_cee_shred = material_dict['Cu_perc_cee_shred']
        Ag_perc_cee_shred = material_dict['Ag_perc_cee_shred']
        Au_perc_cee_shred = material_dict['Au_perc_cee_shred']
        Pd_perc_cee_shred = material_dict['Pd_perc_cee_shred']
        
        Cu_amount_cee_shred_bus = flowAndfactor(o3, Cu_perc_cee_shred)
        Ag_amount_cee_shred_bus = flowAndfactor(o3, Ag_perc_cee_shred)
        Au_amount_cee_shred_bus = flowAndfactor(o3, Au_perc_cee_shred)
        Pd_amount_cee_shred_bus = flowAndfactor(o3, Pd_perc_cee_shred)
        
        sorted_Fe_cee_bus = o1.copy()
        sorted_Al_cee_bus = o2.copy()
        remaining_shredded_materials_cee_bus = o3.copy()
        
        
        #%% part 05 TV shredder bus
        
        # inflow
        tv_pcb_perc = material_dict['tv_pcb_perc']
        
        #outflow
        Fe_perc_tv = material_dict['Fe_perc_tv']
        Al_perc_tv = material_dict['Al_perc_tv']
        remain_material_perc_tv =   np.array([1]*9) - np.array(Fe_perc_tv) - np.array(Al_perc_tv)
        
        
        #stock
        tv_shredder_bus = Stock(inflow = dismantled_materials_bus,
                                 inflow_factors = tv_pcb_perc,
                                 outflow_factors = [Fe_perc_tv, Al_perc_tv, remain_material_perc_tv])
        
        i1 = tv_shredder_bus.inflow
        o1 = tv_shredder_bus.outflow[0]
        o2 = tv_shredder_bus.outflow[1]
        o3 = tv_shredder_bus.outflow[2]
        
        Cu_perc_tv_shred = material_dict['Cu_perc_tv_shred']
        Ag_perc_tv_shred = material_dict['Ag_perc_tv_shred']
        Au_perc_tv_shred = material_dict['Au_perc_tv_shred']
        Pd_perc_tv_shred = material_dict['Pd_perc_tv_shred']
        
        Cu_amount_tv_shred_bus = flowAndfactor(o3, Cu_perc_tv_shred)
        Ag_amount_tv_shred_bus = flowAndfactor(o3, Ag_perc_tv_shred)
        Au_amount_tv_shred_bus = flowAndfactor(o3, Au_perc_tv_shred)
        Pd_amount_tv_shred_bus = flowAndfactor(o3, Pd_perc_tv_shred)
        
        sorted_Fe_tv_shred_bus = o1.copy()
        sorted_Al_tv_shred_bus = o2.copy()
        remaining_shredded_materials_tv_bus = o3.copy()
        
        #%% part 06 Al_at_wh_bus
        
        # inflow
        Al_perc = material_dict['Al_perc']
        i2 = flowSum([sorted_Al_motherboard_bus, sorted_Al_hdd_bus, sorted_Al_tv_shred_bus, sorted_Al_cee_bus])
        
        #stock
        Al_at_wh_bus = Stock(inflow = [dismantled_materials_bus, i2],
                             inflow_factors = [Al_perc, unit_factors],
                             outflow_factors = unit_factors)
        
        sell_to_aluminum_smelters_bus = Al_at_wh_bus.outflow
        
        #%% part 07 Fe_at_wh_bus
        
        # inflow
        Fe_perc = material_dict['Fe_perc']
        i2 = flowSum([sorted_Fe_motherboard_bus, sorted_Fe_hdd_bus, sorted_Fe_tv_shred_bus, sorted_Fe_cee_bus])
        
        #stock
        Fe_at_wh_bus = Stock(inflow = [dismantled_materials_bus, i2],
                             inflow_factors = [Fe_perc, unit_factors],
                             outflow_factors = unit_factors)
        
        sell_to_iron_smelters_bus = Fe_at_wh_bus.outflow
        
        #%% part 08 Cu_at_wh_bus
        
        # inflow
        Cu_perc = material_dict['Cu_perc']
        
        #stock
        Cu_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = Cu_perc,
                             outflow_factors = unit_factors)
        
        sell_to_copper_smelters_bus = Cu_at_wh_bus.outflow
        
        #%% part 09 plastic_at_wh_bus
        
        # inflow
        plastic_perc = material_dict['plastic_perc']
        
        #stock
        plastic_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = plastic_perc,
                             outflow_factors = unit_factors)
        
        sell_to_plastic_recyclers_bus = plastic_at_wh_bus.outflow
        
        #%% part 10 screen_at_wh_bus
        
        # inflow
        screen_perc = material_dict['screen_perc']
        
        #stock
        screen_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = screen_perc,
                             outflow_factors = unit_factors)
        
        send_to_landfill_bus = screen_at_wh_bus.outflow
        
        #%% part 11 CRT_tube_at_wh_bus
        
        # inflow
        CRT_tube_perc = material_dict['CRT_tube_perc']
        
        #stock
        CRT_tube_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = CRT_tube_perc,
                             outflow_factors = unit_factors)
        
        sell_to_Pb_smelters_bus = CRT_tube_at_wh_bus.outflow
        
        #%% part 12 Cu_yoke_at_wh_bus
        
        # inflow
        Cu_yoke_perc = material_dict['Cu_yoke_perc']
        
        #stock
        Cu_yoke_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = Cu_yoke_perc,
                             outflow_factors = unit_factors)
        
        sell_Cu_yoke_bus = Cu_yoke_at_wh_bus.outflow
        
        #%% part 13 degaussing_wire_at_wh_bus
        
        # inflow
        degaussing_wire_perc = material_dict['degaussing_wire_perc']
        
        #stock
        degaussing_wire_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = degaussing_wire_perc,
                             outflow_factors = unit_factors)
        
        sell_degaussing_wire_bus = degaussing_wire_at_wh_bus.outflow
        
        #%% part 14 battery_at_wh_bus
        
        # inflow
        battery_perc = material_dict['battery_perc']
        
        #stock
        battery_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = battery_perc,
                             outflow_factors = unit_factors)
        
        to_battery_recyclers_bus = battery_at_wh_bus.outflow
        
        #%% part 15 cd_rom_wh_bus
        
        # inflow
        cd_rom_perc = material_dict['cd_rom_perc']
        
        #stock
        cd_rom_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = cd_rom_perc,
                             outflow_factors = unit_factors)
        
        sell_CD_rom_bus = cd_rom_at_wh_bus.outflow
        
        #%% part 16 power_sup_wh_bus
        
        # inflow
        power_sup_perc = material_dict['power_sup_perc']
        
        #stock
        power_sup_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = power_sup_perc,
                             outflow_factors = unit_factors)
        
        sell_power_sup_bus = power_sup_at_wh_bus.outflow
        
        #%% part 17 CPU_wh_bus
        
        # inflow
        CPU_perc = material_dict['CPU_perc']
        
        #stock
        CPU_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = CPU_perc,
                             outflow_factors = unit_factors)
        
        sell_CPU_bus = CPU_at_wh_bus.outflow
        
        #%% part 18 RAM_wh_bus
        
        # inflow
        RAM_perc = material_dict['RAM_perc']
        
        #stock
        RAM_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = RAM_perc,
                             outflow_factors = unit_factors)
        
        sell_RAM_bus = RAM_at_wh_bus.outflow
        
        #%% part 19 mixed_pc_wire_bus
        
        # inflow
        mixed_pc_wire_perc = material_dict['mixed_pc_wire_perc']
        
        #stock
        mixed_pc_wire_at_wh_bus = Stock(inflow = dismantled_materials_bus,
                             inflow_factors = mixed_pc_wire_perc,
                             outflow_factors = unit_factors)
        
        sell_mixed_pc_wire_bus = mixed_pc_wire_at_wh_bus.outflow
        
        
        # sell_mixed_pc_wire_bus[item['crt_tv']]
        
        
        
        #=====================================================================================================
        # RESIDENTIAL PART
        #=====================================================================================================
        
        #%% part 01  Inventory_in_wh_res
        
        # inflow
        received_amount_at_wh_res = material_dict['recycled_amount_res']
        
        # outflow
        perc_remarketable_items_res = perc_remarketable_items
        perc_non_marketable_items_res = np.array(unit_factors) - np.array(perc_remarketable_items_res)
        
        o1 = flowAndfactor(received_amount_at_wh_res, perc_remarketable_items_res)
        dismantling_rate_res = [508756,	21976.8,	116868,	27304.2,	73350.8,	8757.12,	86202.5,	61147.9,	61205]  #<<<<<<<<<<<<<<<<<<<<
        
        
        # outflow2 = flowAndfactor(received_amount_at_wh_res, perc_non_marketable_items_res)
        # o2 = np.min([dismantling_rate_res, outflow2], axis = 0)
        o2 = flowAndfactor(received_amount_at_wh_res, perc_non_marketable_items_res)
        
        # stock
        Inventory_in_wh_res = Stock( inflow = received_amount_at_wh_res, initial_stock = [], outflow = [o1, o2] )
        
        sell_to_customers_res =Inventory_in_wh_res.outflow[0]
        dismantled_materials_res = Inventory_in_wh_res.outflow[1]
        
        #%% part 02  Motherboard shredder bus
        
        # # inflow
        # motherboard_perc = [0,	0,	0,	0,	0.094,	0.137,	0,	0,	0]
        
        # # outflow
        # Fe_perc_motherboard = [0,	0,	0,	0,	0.013,	0.037,	0,	0,	0]
        # Al_perc_motherboard = [0,	0,	0,	0,	0.018,	0.018,	0,	0,	0]
        remain_material_perc_motherboard =   np.array([1]*9) - np.array(Fe_perc_motherboard) - np.array(Al_perc_motherboard)
        
        
        #stock
        motherboard_shredder_res = Stock(inflow = dismantled_materials_res,
                                         inflow_factors = motherboard_perc,
                                         outflow_factors = [Fe_perc_motherboard, Al_perc_motherboard, remain_material_perc_motherboard])
        
        i1 = motherboard_shredder_res.inflow
        o1 = motherboard_shredder_res.outflow[0]
        o2 = motherboard_shredder_res.outflow[1]
        o3 = motherboard_shredder_res.outflow[2]
        
        # Cu_perc_motherboard_shred = [0,	0,	0,	0,	0.206,	0.201,	0,	0,	0]
        # Ag_perc_motherboard_shred = [0,	0,	0,	0,	0.000585,	0.001151,	0,	0,	0]
        # Au_perc_motherboard_shred = [0,	0,	0,	0,	0.000246,	0.000659,	0,	0,	0]
        # Pd_perc_motherboard_shred = [0,	0,	0,	0,	0.000154,	0.000209,	0,	0,	0]
        
        Cu_amount_motherboard_shred_res = flowAndfactor(o3, Cu_perc_motherboard_shred)
        Ag_amount_motherboard_shred_res = flowAndfactor(o3, Ag_perc_motherboard_shred)
        Au_amount_motherboard_shred_res = flowAndfactor(o3, Au_perc_motherboard_shred)
        Pd_amount_motherboard_shred_res = flowAndfactor(o3, Pd_perc_motherboard_shred)
        
        sorted_Fe_motherboard_res = o1.copy()
        sorted_Al_motherboard_res = o2.copy()
        remaining_shredded_materials_motherboard_res = o3.copy()
        
        #%% part 03  HDD shredder bus
        
        # # inflow
        # hdd_perc = [0,	0,	0,	0,	0.035,	0.035,	0,	0,	0]
        
        # #outflow
        # Fe_perc_hdd = [0,	0,	0,	0,	0.13,	0.13,	0,	0,	0]
        # Al_perc_hdd = [0,	0,	0,	0,	0.174,	0.174,	0,	0,	0]
        remain_material_perc_hdd =   np.array([1]*9) - np.array(Fe_perc_hdd) - np.array(Al_perc_hdd)
        
        
        #stock
        hdd_shredder_res = Stock(inflow = dismantled_materials_res,
                                 inflow_factors = hdd_perc,
                                 outflow_factors = [Fe_perc_hdd, Al_perc_hdd, remain_material_perc_hdd])
        
        i1 = hdd_shredder_res.inflow
        o1 = hdd_shredder_res.outflow[0]
        o2 = hdd_shredder_res.outflow[1]
        o3 = hdd_shredder_res.outflow[2]
        
        # Cu_perc_hdd_shred = [0,	0,	0,	0,	0.022,	0.022,	0,	0,	0]
        # Ag_perc_hdd_shred = [0,	0,	0,	0,	0.000105,	0.000105,	0,	0,	0]
        # Au_perc_hdd_shred = [0,	0,	0,	0,	1.6e-05,	1.6e-05,	0,	0,	0]
        # Pd_perc_hdd_shred = [0,	0,	0,	0,	1.7e-05,	1.7e-05,	0,	0,	0]
        
        Cu_amount_hdd_shred_res = flowAndfactor(o3, Cu_perc_hdd_shred)
        Ag_amount_hdd_shred_res = flowAndfactor(o3, Ag_perc_hdd_shred)
        Au_amount_hdd_shred_res = flowAndfactor(o3, Au_perc_hdd_shred)
        Pd_amount_hdd_shred_res = flowAndfactor(o3, Pd_perc_hdd_shred)
        
        sorted_Fe_hdd_res = o1.copy()
        sorted_Al_hdd_res = o2.copy()
        remaining_shredded_materials_hdd_res = o3.copy()
        
        
        #%% part 04  Consumer shredder bus
        
        # # inflow
        # cee_perc = [0,	0,	0,	0,	0,	0,	0.074,	0.92,	0.96]
        
        # #outflow
        # Fe_perc_cee = [0,	0,	0,	0,	0,	0,	0.017,	0.3575,	0.1506]
        # Al_perc_cee = [0,	0,	0,	0,	0,	0,	0.18,	0.0301,	0.0301]
        remain_material_perc_cee =   np.array([1]*9) - np.array(Fe_perc_cee) - np.array(Al_perc_cee)
        
        
        #stock
        cee_shredder_res = Stock(inflow = dismantled_materials_res,
                                 inflow_factors = cee_perc,
                                 outflow_factors = [Fe_perc_cee, Al_perc_cee, remain_material_perc_cee])
        
        i1 = cee_shredder_res.inflow
        o1 = cee_shredder_res.outflow[0]
        o2 = cee_shredder_res.outflow[1]
        o3 = cee_shredder_res.outflow[2]
        
        # Cu_perc_cee_shred = [0,	0,	0,	0,	0,	0,	0.174,	0.0998473,	0.0998473]
        # Ag_perc_cee_shred = [0,	0,	0,	0,	0,	0,	8.7e-05,	0.000306147,	0.000306147]
        # Au_perc_cee_shred = [0,	0,	0,	0,	0,	0,	4.7e-05,	7.35848e-05,	7.35848e-05]
        # Pd_perc_cee_shred = [0,	0,	0,	0,	0,	0,	2.6e-05,	2.11199e-05,	2.11199e-05]
        
        Cu_amount_cee_shred_res = flowAndfactor(o3, Cu_perc_cee_shred)
        Ag_amount_cee_shred_res = flowAndfactor(o3, Ag_perc_cee_shred)
        Au_amount_cee_shred_res = flowAndfactor(o3, Au_perc_cee_shred)
        Pd_amount_cee_shred_res = flowAndfactor(o3, Pd_perc_cee_shred)
        
        sorted_Fe_cee_res = o1.copy()
        sorted_Al_cee_res = o2.copy()
        remaining_shredded_materials_cee_res = o3.copy()
        
        
        #%% part 05 TV shredder bus
        
        # # inflow
        # tv_pcb_perc = [0.023,	0.023,	0.077,	0.06,	0,	0,	0,	0,	0]
        
        # #outflow
        # Fe_perc_tv = [0.034,	0.034,	0.049,	0.049,	0,	0,	0,	0,	0]
        # Al_perc_tv = [0.062,	0.062,	0.063,	0.063,	0,	0,	0,	0,	0]
        remain_material_perc_tv =   np.array([1]*9) - np.array(Fe_perc_tv) - np.array(Al_perc_tv)
        
        
        #stock
        tv_shredder_res = Stock(inflow = dismantled_materials_res,
                                 inflow_factors = tv_pcb_perc,
                                 outflow_factors = [Fe_perc_tv, Al_perc_tv, remain_material_perc_tv])
        
        i1 = tv_shredder_res.inflow
        o1 = tv_shredder_res.outflow[0]
        o2 = tv_shredder_res.outflow[1]
        o3 = tv_shredder_res.outflow[2]
        
        # Cu_perc_tv_shred = [0.08,	0.08,	0.203,	0.203,	0,	0,	0,	0,	0]
        # Ag_perc_tv_shred = [0.000132,	0.000132,	0.000659,	0.000659,	0,	0,	0,	0,	0]
        # Au_perc_tv_shred = [5.48e-06,	5.48e-06,	0.00021952,	0.00021952,	0,	0,	0,	0,	0]
        # Pd_perc_tv_shred = [2.193e-05,	2.193e-05,	0,	0,	0,	0,	0,	0,	0]
        
        Cu_amount_tv_shred_res = flowAndfactor(o3, Cu_perc_tv_shred)
        Ag_amount_tv_shred_res = flowAndfactor(o3, Ag_perc_tv_shred)
        Au_amount_tv_shred_res = flowAndfactor(o3, Au_perc_tv_shred)
        Pd_amount_tv_shred_res = flowAndfactor(o3, Pd_perc_tv_shred)
        
        sorted_Fe_tv_shred_res = o1.copy()
        sorted_Al_tv_shred_res = o2.copy()
        remaining_shredded_materials_tv_res = o3.copy()
        
        #%% part 06 Al_at_wh_res
        
        # inflow
        # Al_perc = [0.003,	0.003,	0.014,	0.029,	0,	0.024,	0.002,	0,	0]
        i2 = flowSum([sorted_Al_motherboard_res, sorted_Al_hdd_res, sorted_Al_tv_shred_res, sorted_Al_cee_res])
        
        #stock
        Al_at_wh_res = Stock(inflow = [dismantled_materials_res, i2],
                             inflow_factors = [Al_perc, unit_factors],
                             outflow_factors = unit_factors)
        
        sell_to_aluminum_smelters_res = Al_at_wh_res.outflow
        
        #%% part 07 Fe_at_wh_res
        
        # inflow
        # Fe_perc = [0.036,	0.036,	0.373,	0.384,	0.472,	0.195,	0.355,	0,	0]
        i2 = flowSum([sorted_Fe_motherboard_res, sorted_Fe_hdd_res, sorted_Fe_tv_shred_res, sorted_Fe_cee_res])
        
        #stock
        Fe_at_wh_res = Stock(inflow = [dismantled_materials_res, i2],
                             inflow_factors = [Fe_perc, unit_factors],
                             outflow_factors = unit_factors)
        
        sell_to_iron_smelters_res = Fe_at_wh_res.outflow
        
        #%% part 08 Cu_at_wh_res
        
        # inflow
        # Cu_perc = [0,	0,	0.004,	0.051,	0.009,	0.01,	0.032,	0,	0]
        
        #stock
        Cu_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = Cu_perc,
                             outflow_factors = unit_factors)
        
        sell_to_copper_smelters_res = Cu_at_wh_res.outflow
        
        #%% part 09 plastic_at_wh_res
        
        # inflow
        # plastic_perc = [0.197,	0.197,	0.316,	0.248,	0.028,	0.258,	0.458,	0,	0]
        
        #stock
        plastic_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = plastic_perc,
                             outflow_factors = unit_factors)
        
        sell_to_plastic_recyclers_res = plastic_at_wh_res.outflow
        
        #%% part 10 screen_at_wh_res
        
        # inflow
        # screen_perc = [0,	0,	0.215,	0.208,	0,	0,	0,	0,	0]
        
        #stock
        screen_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = screen_perc,
                             outflow_factors = unit_factors)
        
        send_to_landfill_res = screen_at_wh_res.outflow
        
        #%% part 11 CRT_tube_at_wh_res
        
        # inflow
        # CRT_tube_perc = [0.696,	0.696,	0,	0,	0,	0,	0,	0,	0]
        
        #stock
        CRT_tube_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = CRT_tube_perc,
                             outflow_factors = unit_factors)
        
        sell_to_Pb_smelters_res = CRT_tube_at_wh_res.outflow
        
        #%% part 12 Cu_yoke_at_wh_res
        
        # inflow
        # Cu_yoke_perc = [0.024,	0.024,	0,	0,	0,	0,	0,	0,	0]
        
        #stock
        Cu_yoke_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = Cu_yoke_perc,
                             outflow_factors = unit_factors)
        
        sell_Cu_yoke_res = Cu_yoke_at_wh_res.outflow
        
        #%% part 13 degaussing_wire_at_wh_res
        
        # inflow
        # degaussing_wire_perc = [0.0104,	0.0104,	0,	0,	0,	0,	0,	0,	0]
        
        #stock
        degaussing_wire_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = degaussing_wire_perc,
                             outflow_factors = unit_factors)
        
        sell_degaussing_wire_res = degaussing_wire_at_wh_res.outflow
        
        #%% part 14 battery_at_wh_res
        
        # inflow
        # battery_perc = [0,	0,	0,	0,	0,	0.135,	0,	0.8,	0.04]
        
        #stock
        battery_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = battery_perc,
                             outflow_factors = unit_factors)
        
        to_battery_recyclers_res = battery_at_wh_res.outflow
        
        #%% part 15 cd_rom_wh_res
        
        # inflow
        # cd_rom_perc = [0,	0,	0,	0,	0.1343,	0.1343,	0,	0,	0]
        
        #stock
        cd_rom_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = cd_rom_perc,
                             outflow_factors = unit_factors)
        
        sell_CD_rom_res = cd_rom_at_wh_res.outflow
        
        #%% part 16 power_sup_wh_res
        
        # inflow
        # power_sup_perc = [0,	0,	0,	0,	0.1446,	0,	0,	0,	0]
        
        #stock
        power_sup_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = power_sup_perc,
                             outflow_factors = unit_factors)
        
        sell_power_sup_res = power_sup_at_wh_res.outflow
        
        #%% part 17 CPU_wh_res
        
        # inflow
        # CPU_perc = [0,	0,	0,	0,	0.0031,	0.0031,	0,	0,	0]
        
        #stock
        CPU_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = CPU_perc,
                             outflow_factors = unit_factors)
        
        sell_CPU_res = CPU_at_wh_res.outflow
        
        #%% part 18 RAM_wh_res
        
        # inflow
        # RAM_perc = [0,	0,	0,	0,	0.0103,	0.0103,	0,	0,	0]
        
        #stock
        RAM_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = RAM_perc,
                             outflow_factors = unit_factors)
        
        sell_RAM_res = RAM_at_wh_res.outflow
        
        #%% part 19 mixed_pc_wire_res
        
        # inflow
        # mixed_pc_wire_perc = [0,	0,	0,	0,	0.0413,	0,	0,	0,	0]
        
        #stock
        mixed_pc_wire_at_wh_res = Stock(inflow = dismantled_materials_res,
                             inflow_factors = mixed_pc_wire_perc,
                             outflow_factors = unit_factors)
        
        sell_mixed_pc_wire_res = mixed_pc_wire_at_wh_res.outflow
        
        
        
        
        
        
        #============================================================================================
        # WINDOW -2: COST CALCULATION
        #============================================================================================        
        
        # FIXED MANUFACTURING OVERHEAD PER LB=================================================
        total_fixed_manufacturing_overhead_per_month = cost_dict['Total fixed manufacturing overhead per month']
        overhead_adjustment_factor = cost_dict['Fraction of overhead cost coming from top e-waste items']
        adjusted_total_fixed_manufacturing_overhead_per_month = flowProduct([total_fixed_manufacturing_overhead_per_month,
                                                                             overhead_adjustment_factor])
        
        if self.get_data_from_process_model:
            recycled_amount_item_wise = self.recycled_amount_item_wise
        else:
            recycled_amount_item_wise = flowSum([material_dict['recycled_amount_bus'],
                                                 material_dict['recycled_amount_res']])
        
        
        fixed_manufacturing_overhead_per_lb = flowDivide(adjusted_total_fixed_manufacturing_overhead_per_month,
                                                         dissolveSubs(recycled_amount_item_wise) )
        fixed_manufacturing_overhead_per_lb = fixed_manufacturing_overhead_per_lb * len(unit_factors) #add subscripts
        
        
        # VARIABLE MANUFACTURING OVERHEAD=================================================
        
        #repair_and_maintenance_cost_per_lb
        repair_and_maintenance_cost_per_month = cost_dict['Repair and maintenance cost per month']
        adjusted_repair_and_maintenance_cost_per_month = flowProduct( [repair_and_maintenance_cost_per_month,
                                                                       overhead_adjustment_factor] )
        repair_and_maintenance_cost_per_lb = flowDivide(adjusted_repair_and_maintenance_cost_per_month,
                                                         dissolveSubs(recycled_amount_item_wise) )
        
        
        # wareoperating cost per lb
        warehouse_operating_cost_per_month = cost_dict['Warehouse misc operating cost per month']
        adjusted_warehouse_operating_cost_per_month = flowProduct( [warehouse_operating_cost_per_month,
                                                                    overhead_adjustment_factor] )
        
        warehouse_operating_cost_per_lb = flowDivide(adjusted_warehouse_operating_cost_per_month,
                                                     dissolveSubs(recycled_amount_item_wise) )
        
        
        # transportation cost per lb
        transportation_cost_per_month = cost_dict['Transportation cost per month']
        
        adjusted_transportation_cost_per_month = flowProduct( [transportation_cost_per_month,
                                                                     overhead_adjustment_factor] )
        
        transportation_cost_per_lb = flowDivide(adjusted_transportation_cost_per_month,
                                                dissolveSubs(recycled_amount_item_wise) )

        
        if self.get_data_from_process_model:
            # processing_cost_per_lb_without_overhead_itemwise already considers machine energy cost
            # deduct machine energy cost so that it is not counted twice 
            utility_cost_per_month = list(  np.array(cost_dict['Utility cost per month']) * (1 - self.d.cost_dict['fraction_of_utility_cost_from_shop_floor_machines'])  )
            
        else:
            utility_cost_per_month = cost_dict['Utility cost per month']
            
            
        adjusted_utility_cost_per_month = flowProduct( [utility_cost_per_month,
                                                        overhead_adjustment_factor] )
        
        utility_cost_per_lb = flowDivide(adjusted_utility_cost_per_month,
                                         dissolveSubs(recycled_amount_item_wise) )
        
        
        
        variable_manufacturing_overhead_per_lb = flowSum([repair_and_maintenance_cost_per_lb,
                                                          warehouse_operating_cost_per_lb,
                                                          transportation_cost_per_lb,
                                                          utility_cost_per_lb])
        
        variable_manufacturing_overhead_per_lb = variable_manufacturing_overhead_per_lb * len(unit_factors)  # #add subscripts
        
        
        manufacturing_overhead_per_lb = flowSum([fixed_manufacturing_overhead_per_lb,
                                                 variable_manufacturing_overhead_per_lb])
            
        if not self.get_data_from_process_model:
            
            # ADJUSTED BATTERY TREATMENT COST PER LB =================================================
            battery_perc = material_dict['battery_perc']
            if len(cost_dict['Battery treatment cost per lb']) == 1: # when input data is from the GUI
                cost_dict['Battery treatment cost per lb'] = cost_dict['Battery treatment cost per lb'] * len(keys)
            battery_treatment_cost_per_lb = cost_dict['Battery treatment cost per lb']
            adjusted_battery_treatment_cost_per_lb = flowProduct([battery_treatment_cost_per_lb,
                                                                   battery_perc])
            
            # ADJUSTED CRT TUBE TREATMENT COST PER LB =================================================
            CRT_tube_perc = material_dict['CRT_tube_perc']
            if len(cost_dict['CRT tube treatment cost per lb']) == 1: # when input data is from the GUI
                cost_dict['CRT tube treatment cost per lb'] = cost_dict['CRT tube treatment cost per lb'] * len(keys)
            CRT_tube_treatment_cost_per_lb = cost_dict['CRT tube treatment cost per lb']
            adjusted_CRT_tube_treatment_cost_per_lb = flowProduct([CRT_tube_treatment_cost_per_lb,
                                                                   CRT_tube_perc])
            
            
            
            # PROCESSING LABOR COST PER LB =================================================
            
            # sorting labor cost per lb
            total_sorting_labor_cost_per_month = cost_dict['Total sorting labor cost per month']
            adjusted_total_sorting_labor_cost_per_month = flowProduct([overhead_adjustment_factor,
                                                                       total_sorting_labor_cost_per_month])
            
            sorting_labor_cost_per_lb = flowDivide(adjusted_total_sorting_labor_cost_per_month,
                                                   dissolveSubs(recycled_amount_item_wise))
            sorting_labor_cost_per_lb = sorting_labor_cost_per_lb * len(unit_factors)
            
            
            # dismantling_labor_cost_per_lb
            dismantling_time_per_item_in_minutes = material_dict['dismantling_time_per_item_in_minutes']
            mass_per_item_in_lbs = material_dict['weight_per_item_in_lbs']
            dismantling_time_per_lb = flowDivide(dismantling_time_per_item_in_minutes,
                                                 mass_per_item_in_lbs)
            minutes_to_hours = [1/60] * len(unit_factors)
            dismantling_man_hours_item_wise = flowProduct([dismantling_time_per_lb,
                                                           recycled_amount_item_wise,
                                                           minutes_to_hours])
            
            percent_dismantling_man_hours_item_wise = flowDivide(dismantling_man_hours_item_wise,
                                                                 dissolveSubs(dismantling_man_hours_item_wise))
            
            total_dismantling_labor_cost_per_month = cost_dict['Total dismantling labor cost per month']
            
            adjusted_dismantling_labor_cost_per_month = flowProduct([total_dismantling_labor_cost_per_month,
                                                                     overhead_adjustment_factor])
            adjusted_dismantling_labor_cost_per_month = adjusted_dismantling_labor_cost_per_month * len(unit_factors)
            
            dismantling_labor_cost_per_month_item_wise = flowProduct([percent_dismantling_man_hours_item_wise,
                                                                      adjusted_dismantling_labor_cost_per_month])
            
            dismantling_labor_cost_per_lb = flowDivide(dismantling_labor_cost_per_month_item_wise,
                                                       recycled_amount_item_wise)
            
            
            # shredding_labor_cost_per_lb
            tv_pcb_perc         = material_dict['tv_pcb_perc']
            motherboard_perc    = material_dict['motherboard_perc']
            hdd_perc            = material_dict['hdd_perc']
            # cee_perc            = material_dict['cee_perc']
            
            amount_to_be_shredded = flowProduct([recycled_amount_item_wise,
                                                 flowSum([tv_pcb_perc, motherboard_perc, hdd_perc, cee_perc])])
            
            
            total_shredding_labor_cost_per_month = cost_dict['Total shredding labor cost per month']
            adjusted_total_shredding_labor_cost_per_month = flowProduct([total_shredding_labor_cost_per_month,
                                                                         overhead_adjustment_factor])
            
            adjusted_total_shredding_labor_cost_per_month = adjusted_total_shredding_labor_cost_per_month * len(unit_factors)
            
            shredding_labor_cost_item_wise = flowProduct([flowDivide(amount_to_be_shredded, dissolveSubs(amount_to_be_shredded)),
                                                          adjusted_total_shredding_labor_cost_per_month])
            
            shredding_labor_cost_per_lb = flowDivide(shredding_labor_cost_item_wise, recycled_amount_item_wise)
            
            processing_labor_cost_per_lb = flowSum([sorting_labor_cost_per_lb,
                                                    dismantling_labor_cost_per_lb,
                                                    shredding_labor_cost_per_lb])
            
            
            
            processing_cost_per_lb_without_overhead_itemwise = flowSum([adjusted_battery_treatment_cost_per_lb,
                                                                       adjusted_CRT_tube_treatment_cost_per_lb,
                                                                       processing_labor_cost_per_lb])
        
        if self.get_data_from_process_model:
            processing_cost_per_lb_without_overhead_itemwise = self.processing_cost_per_lb_without_overhead_itemwise
            
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++
        processing_cost_per_lb_item_wise = flowSum([manufacturing_overhead_per_lb,
                                                   processing_cost_per_lb_without_overhead_itemwise])
        
        
        
        
        # OVERALL PROCESSING COST PER LB =================================================
        processing_cost_per_month_item_wise = flowProduct([recycled_amount_item_wise,
                                                           processing_cost_per_lb_item_wise])
        
        processing_cost_per_month = dissolveSubs(processing_cost_per_month_item_wise)
        total_recycled_amount = dissolveSubs(recycled_amount_item_wise)
        overall_processing_cost_per_lb = flowDivide(processing_cost_per_month,
                                                    total_recycled_amount)[0]
        
        
        
        #set class attributes
        self.processing_cost_per_lb_item_wise  = processing_cost_per_lb_item_wise 
        self.processing_cost_per_month_item_wise = processing_cost_per_month_item_wise
        self.processing_cost_per_month = processing_cost_per_month
        self.overall_processing_cost_per_lb = overall_processing_cost_per_lb
        
        
        
        #============================================================================================
        # WINDOW -3: REVENUE CALCULATION
        #============================================================================================

        # environmental revenue
        environmental_fee_per_lb = price_dict['environmental_fee_per_lb']
        total_ewaste_amount_item_wise = recycled_amount_item_wise
        
        
        # environmental_revenue
        environmental_revenue = Revenue(material_amount = total_ewaste_amount_item_wise,
                                        per_unit_price = environmental_fee_per_lb).revenue
        
        
        # aluminum_revenue
        aluminum_revenue = Revenue(material_amount = [sell_to_aluminum_smelters_bus, 
                                                  sell_to_aluminum_smelters_res],
                               per_unit_price = price_dict['aluminum_price']).revenue
        
        
        
        # copper_revenue
        copper_revenue = Revenue(material_amount = [sell_to_copper_smelters_bus, 
                                                  sell_to_copper_smelters_res],
                               per_unit_price = price_dict['copper_price']).revenue
        
        
        # iron_revenue
        iron_revenue = Revenue(material_amount = [sell_to_iron_smelters_bus, 
                                                  sell_to_iron_smelters_res],
                               per_unit_price = price_dict['iron_price']).revenue
        
        
        
        # plastic_revenue
        plastic_revenue = Revenue(material_amount = [sell_to_plastic_recyclers_bus, 
                                                  sell_to_plastic_recyclers_res],
                               per_unit_price = price_dict['plastic_price']).revenue
        
        
        
        # copper_yoke_revenue
        copper_yoke_revenue = Revenue(material_amount = [sell_Cu_yoke_bus, 
                                                  sell_Cu_yoke_res],
                               per_unit_price = price_dict['copper_yoke_price']).revenue
        
        
        # degaussing_wire_revenue
        degaussing_wire_revenue = Revenue(material_amount = [sell_degaussing_wire_bus, 
                                                  sell_degaussing_wire_res],
                               per_unit_price = price_dict['degaussing_wire_price']).revenue
        
        
        # cd_rom_revenue
        cd_rom_revenue = Revenue(material_amount = [sell_CD_rom_bus, 
                                                  sell_CD_rom_res],
                               per_unit_price = price_dict['cd_rom_price']).revenue
        
        
        # power_sup_revenue
        power_sup_revenue = Revenue(material_amount = [sell_power_sup_bus, 
                                                  sell_power_sup_res],
                               per_unit_price = price_dict['power_sup_price']).revenue
        
        
        # cpu_revenue
        cpu_revenue = Revenue(material_amount = [sell_CPU_bus, 
                                                  sell_CPU_res],
                               per_unit_price = price_dict['cpu_price']).revenue
        
        
        # ram_revenue
        ram_revenue = Revenue(material_amount = [sell_RAM_bus, 
                                                  sell_RAM_res],
                               per_unit_price = price_dict['ram_price']).revenue
        
        # mixed_pc_wire_revenue
        mixed_pc_wire_revenue = Revenue(material_amount = [sell_mixed_pc_wire_bus, 
                                                  sell_mixed_pc_wire_res],
                               per_unit_price = price_dict['mixed_pc_wire_price']).revenue
        
        
        ## Revenue from Shred------------------------------------------------------------------
        # copper_revenue_from_shred
        copper_revenue_from_shred = Revenue(material_amount = [Cu_amount_motherboard_shred_bus,
                                                               Cu_amount_motherboard_shred_res,
                                                               Cu_amount_hdd_shred_bus,
                                                               Cu_amount_hdd_shred_res,
                                                               Cu_amount_cee_shred_bus,
                                                               Cu_amount_cee_shred_res,
                                                               Cu_amount_tv_shred_bus,
                                                               Cu_amount_tv_shred_res],
                               per_unit_price = price_dict['copper_price']).revenue
        
        
        # silver_revenue_from_shred
        silver_revenue_from_shred = Revenue(material_amount = [Ag_amount_motherboard_shred_bus,
                                                               Ag_amount_motherboard_shred_res,
                                                               Ag_amount_hdd_shred_bus,
                                                               Ag_amount_hdd_shred_res,
                                                               Ag_amount_cee_shred_bus,
                                                               Ag_amount_cee_shred_res,
                                                               Ag_amount_tv_shred_bus,
                                                               Ag_amount_tv_shred_res],
                               per_unit_price = price_dict['silver_price']).revenue
        
        
        # gold_revenue_from_shred
        gold_revenue_from_shred = Revenue(material_amount = [  Au_amount_motherboard_shred_bus,
                                                               Au_amount_motherboard_shred_res,
                                                               Au_amount_hdd_shred_bus,
                                                               Au_amount_hdd_shred_res,
                                                               Au_amount_cee_shred_bus,
                                                               Au_amount_cee_shred_res,
                                                               Au_amount_tv_shred_bus,
                                                               Au_amount_tv_shred_res],
                                          per_unit_price = price_dict['gold_price']).revenue
        
        
        # palladium_revenue_from_shred
        palladium_revenue_from_shred = Revenue(material_amount = [Pd_amount_motherboard_shred_bus,
                                                                  Pd_amount_motherboard_shred_res,
                                                                  Pd_amount_hdd_shred_bus,
                                                                  Pd_amount_hdd_shred_res,
                                                                  Pd_amount_cee_shred_bus,
                                                                  Pd_amount_cee_shred_res,
                                                                  Pd_amount_tv_shred_bus,
                                                                  Pd_amount_tv_shred_res],
                                               per_unit_price = price_dict['palladium_price']).revenue
        
        
        
        ## Fees and Freight Charged by Refiners------------------------------------------------------
        # hdd_shred_fees_and_freight
        hdd_shred_fees_and_freight = Revenue(material_amount = [remaining_shredded_materials_hdd_bus,
                                                                remaining_shredded_materials_hdd_res],
                                             per_unit_price = price_dict['hdd_shred_fees_and_freight_per_lb']).revenue
        
        
        # cee_shred_fees_and_freight
        cee_shred_fees_and_freight = Revenue(material_amount = [remaining_shredded_materials_cee_bus,
                                                                remaining_shredded_materials_cee_res],
                                             per_unit_price = price_dict['cee_shred_fees_and_freight_per_lb']).revenue
        
        # motherboard_shred_fees_and_freight
        motherboard_shred_fees_and_freight = Revenue(material_amount = [remaining_shredded_materials_motherboard_bus,
                                                                remaining_shredded_materials_motherboard_res],
                                             per_unit_price = price_dict['motherboard_shred_fees_and_freight_per_lb']).revenue
        
        
        # tv_shred_fees_and_freight
        tv_shred_fees_and_freight = Revenue(material_amount = [remaining_shredded_materials_tv_bus,
                                                                remaining_shredded_materials_tv_res],
                                             per_unit_price = price_dict['tv_shred_fees_and_freight_per_lb']).revenue
        
        
        
        ## Net Revenue from Shred------------------------------------------------------------------
        revenue_from_shred = flowSum([copper_revenue_from_shred,
                                      silver_revenue_from_shred,
                                      gold_revenue_from_shred,
                                      palladium_revenue_from_shred])
                                     
        
        fees_and_freight_from_shred = flowSum([hdd_shred_fees_and_freight,
                                               cee_shred_fees_and_freight,
                                               motherboard_shred_fees_and_freight,
                                               tv_shred_fees_and_freight])
        
        
        net_revenue_from_shred = ( np.array(revenue_from_shred) - np.array(fees_and_freight_from_shred) ).tolist()
        
        
        ## Finl Revenue and Profit
        total_revenue_item_wise = flowSum([net_revenue_from_shred,
                                           environmental_revenue,
                                           aluminum_revenue,
                                           copper_revenue,
                                           iron_revenue,
                                           plastic_revenue,
                                           copper_yoke_revenue,
                                           degaussing_wire_revenue,
                                           cd_rom_revenue,
                                           power_sup_revenue,
                                           cpu_revenue,
                                           ram_revenue,
                                           mixed_pc_wire_revenue])
        
        
        revenue_per_lb_item_wise = np.round(( np.array(total_revenue_item_wise) / np.array(total_ewaste_amount_item_wise) ).tolist(), 4)
        
        revenue_per_lb_overall = sum(total_revenue_item_wise) / sum(total_ewaste_amount_item_wise)
        
        
        
        
        profit_item_wise = flowSubtract(total_revenue_item_wise,
                                        processing_cost_per_month_item_wise)
        
        
        profit_per_lb_item_wise = flowDivide(profit_item_wise,
                                             recycled_amount_item_wise)
        
        
        profit_per_lb_overall = flowDivide(dissolveSubs( flowProduct([profit_per_lb_item_wise, recycled_amount_item_wise]) ),
                                           dissolveSubs(recycled_amount_item_wise))[0]


        # set class attributes
        self.revenue_per_lb_item_wise = revenue_per_lb_item_wise
        self.revenue_per_lb_overall = revenue_per_lb_overall
        self.profit_item_wise = profit_item_wise
        self.profit_per_lb_item_wise = profit_per_lb_item_wise
        self.profit_per_lb_overall = profit_per_lb_overall



    def run_economic_model(self):
        try:
            self.do_calculations()
            
            self.text = f"\n\
Overall Statistics \n\
------------------ \n\
Overall revenue per lb ($/lb)             :{self.revenue_per_lb_overall : .2f}\n\
Overall processing cost per lb ($/lb)     :{self.overall_processing_cost_per_lb : .2f}\n\
Overall profit per lb ($/lb)              :{self.profit_per_lb_overall : .2f}\n\n\n\
Item-Wise Statistics: \n"

        
            row1 = ['Revenue per lb']
            row2 = ['Processing cost per lb']
            row3 = ['Profit per lb']
            for r1, r2, r3 in zip(self.revenue_per_lb_item_wise, self.processing_cost_per_lb_item_wise, self.profit_per_lb_item_wise) :
                row1.append(round(r1, 2))
                row2.append(round(r2, 2))
                row3.append(round(r3, 2))
            
            table = [row1, row2, row3]
            headers = [' ', 'CRT TV', 'CRT Monitor', 'LCD TV', 'LCD Monitor', 'Desktop', 'Laptop', 'Printer', 'Small CEE', 'Computer\nPeripherals']
            self.text += tabulate(table, headers, tablefmt="psql")
        
        except Exception as e: 
            self.text = f'{type(e).__name__}: {e.args}'
            
     

    def create_plot(self):
        ## itemwise revenue, cost, and profit
        fig = plt.figure(dpi = 300, figsize =(8, 4), constrained_layout=True )
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        revenue = self.revenue_per_lb_item_wise
        cost = self.processing_cost_per_lb_item_wise
        profit = self.profit_per_lb_item_wise
        
        
        labels = ['CRT TV', 'CRT Monitor', 'LCD TV', 'LCD Monitor', 'Desktop', 'Laptop', 'Printer', 'Small CEE', 'Computer Peripherals']
        x = np.arange(len(labels))  # X tick label locations
        width = 0.25  # the width of the bars
        color = ['deepskyblue', 'orangered', 'orange',]
        
        b1 = ax.bar(x - 1*width, revenue, width = width, color = color[0], alpha = 1.0, label='Revenue')
        b2 = ax.bar(x + 0*width, cost, width = width, color = color[1], alpha = 1.0, label='Procecssing Cost')
        b3 = ax.bar(x + 1*width, profit, width = width, color = color[2], alpha = 1.0, label='Profit')
        
        ax.set_ylabel('$/lb', fontweight = 'bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels=labels, rotation=45, ha='right', fontweight = 'regular', fontsize=12)
        ax.legend(bbox_to_anchor=(0.00, 1.15), loc='upper left', ncol=3, fontsize=12)
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.2f}'))
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # # define a function for auto labeling
        # def auto_label(ax, bars):
        #     """
        #     Attach a text label above each bar displaying its height
        #     """
        #     for bar in bars:
        #         height = bar.get_height()
        #         ax.text(bar.get_x() + bar.get_width()/2, 0.00*height,
        #                 f'{height : .3f}',
        #                 ha='center', va='bottom',
        #                 rotation=90, color = 'k', fontsize=8, fontweight = 'regular') 
                
        # auto_label(ax, b1)
        # auto_label(ax, b2)
        # auto_label(ax, b3)
        
        ## Overall revenue, cost, and profit
        fig = plt.figure(dpi = 300, figsize =(8, 4), constrained_layout=True )
        gs = GridSpec(1, 1, figure=fig)
        ax = fig.add_subplot(gs[0, 0])
        
        x = ['Overall Revenue', 'Overall Cost', 'Overall Profit',]
        # x = np.arange(len(keys))  # X tick label locations
        y = [self.revenue_per_lb_overall,
             self.overall_processing_cost_per_lb,
             self.profit_per_lb_overall
             ]
        
        width = 0.25  # the width of the bars  
        
        b = ax.bar(x, y, width = width, color = 'dodgerblue', alpha = 1.0)
        ax.set_ylabel('$/lb', fontweight = 'bold', fontsize=12)
        ax.set_xticklabels(labels=x, rotation=0, ha='center', fontweight = 'regular', fontsize=12)
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.2f}'))
        ax.tick_params(axis='both', which='major', labelsize=12)
       
        # define a function for auto labeling
        def auto_label(ax, bars):
            """
            Attach a text label above each bar displaying its height
            """
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, 0.00*height,
                        f'{height : .3f}',
                        ha='center', va='bottom',
                        rotation=90, color = 'k', fontsize=12, fontweight = 'regular') 
                
        auto_label(ax, b)
        

#%%
if __name__ == "__main__":
    # track program run time
    start_time = time.time()
        
    # create data
    data = EconomicData(excel_file_name = 'TEMPLATE_economic_model_data.xlsx')
    
    # create economic model
    em = EconomicModel(data, get_data_from_process_model = False)
    # run the model
    em.run_economic_model()
    
    #print some statistics
    print(em.text)
    em.create_plot()

    #calculate program run time
    end_time = time.time()
    run_time = np.round((end_time - start_time), 4)
    print(f'\nProgram run time: {run_time} seconds')
    
    




    
    
