"""
@author: Mamunur Rahman
"""

import simpy
import random
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys



# progress bar
def progress_bar(total_iteration, current_iteration):
    barLength = 50
    status = "complete"
    current_iteration1 = current_iteration
    current_iteration = current_iteration / total_iteration
    if current_iteration >= 1:
        status = "complete\r\n"
    block = int(round(barLength * current_iteration))
    percent_complete = round(current_iteration * 100, 0)
    text = f'\rProgress: [{"#" * block + "=" * (barLength - block)}][{current_iteration1}/{total_iteration} mins]{percent_complete: .0f}% {status}'
    sys.stdout.write(text)
    sys.stdout.flush()



# find the name of the target output queue based on 'OUTPUT QUEUE PROBABILITY' and product category
def target_output_queue_name(data, product):
    # generate a random number
    x = random.random()
    
    # queue list
    queue_list = data['OUTPUT QUEUE NAMES']
    
    cum_prob = 0
    for idx, queue in enumerate(queue_list):
        cum_prob += data['OUTPUT QUEUE PROBABILITY'][product.category][idx]    
        if x <= cum_prob:
            target_queue_name = queue
            break
    
    return target_queue_name




def read_manual_work_station_data(excel_file_name, sheet_name):
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name, header = None)
    
    
    work_station_data = {}
    
    # TYPE, NAME, NO OF OPERATORS, OPERATOR WAGE RATE, INPUT QUEUE CAPACITY
    for i in range(5):
        work_station_data[df.iloc[i, 0]] = df.iloc[i, 1]
    
    # PROCESSING TIME
    values = df.iloc[6, 1:]
    keys = df.iloc[5, 1:]
    work_station_data['PROCESSING TIME'] = dict( zip(keys, values) )
    
    # NON SHREDDABLE OUTPUT PROBABILITY
    values = df.iloc[7, 1:]
    work_station_data['NON SHREDDABLE OUTPUT PROBABILITY'] = dict( zip(keys, values) )
    
    # NON SHREDDABLE OUTPUT FRACTION
    values = df.iloc[8, 1:]
    work_station_data['NON SHREDDABLE OUTPUT PERCENTAGE'] = dict( zip(keys, values) )
    
    # OUTPUT QUEUE NAMES
    output_queue_names = df.iloc[9, 1:].to_list()
    output_queue_names = [x for x in output_queue_names if str(x) != 'nan']  # remove nan values
    work_station_data['OUTPUT QUEUE NAMES'] = output_queue_names
    
    # OUTPUT QUEUE CAPACITIES
    output_queue_capacities = df.iloc[10, 1:].to_list()
    output_queue_capacities = [x for x in output_queue_capacities if str(x) != 'nan']  # remove nan values
    work_station_data['OUTPUT QUEUE CAPACITIES'] = output_queue_capacities
    
    # OUTPUT QUEUE PROBABILITY
    output_queue_probability = {}
    no_of_product_categories = len( work_station_data['PROCESSING TIME'].keys() )
    
    for i in range(12, 12 + no_of_product_categories):
        key = df.iloc[i, 0]
        value = df.iloc[i, 1 : len(output_queue_names) + 1].to_list()
        output_queue_probability[key] = value
    
    work_station_data['OUTPUT QUEUE PROBABILITY'] = output_queue_probability
    
    return work_station_data



def read_dismantling_station_data(excel_file_name, sheet_name):
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name, header = None)
    
    
    data = {}
    
    # TYPE, NAME, NO OF OPERATORS, OPERATOR WAGE RATE, INPUT QUEUE CAPACITY
    for i in range(5):
        data[df.iloc[i, 0]] = df.iloc[i, 1]
    
    # PROCESSING TIME
    values = df.iloc[6, 1:]
    keys = df.iloc[5, 1:]
    data['PROCESSING TIME'] = dict( zip(keys, values) )
    
    # NON SHREDDABLE OUTPUT PROBABILITY
    values = df.iloc[7, 1:]
    data['NON SHREDDABLE OUTPUT PROBABILITY'] = dict( zip(keys, values) )
    
    # NON SHREDDABLE OUTPUT FRACTION
    values = df.iloc[8, 1:]
    data['NON SHREDDABLE OUTPUT PERCENTAGE'] = dict( zip(keys, values) )
    
    # OUTPUT QUEUE NAMES
    data['OUTPUT QUEUE NAME'] = df.iloc[9, 1]
    
    # OUTPUT QUEUE CAPACITIES
    data['OUTPUT QUEUE CAPACITY'] = df.iloc[10, 1]
        
    return data
 


def read_product_source_data(excel_file_name, sheet_name):
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name, header = None)
  
    data = {}
    
    # TYPE, NAME, INITIAL LOCATION
    data['TYPE']                = df.iloc[0, 1]
    data['NAME']                = df.iloc[1, 1]
    data['INITIAL LOCATION']    = df.iloc[2, 1]
    data['PRODUCT AMOUNT']      = df.iloc[3, 1]
    
    # PRODUCT MASS
    keys = df.iloc[4, 1:]
    values = df.iloc[5, 1:]    
    data['PRODUCT MASS'] = dict( zip(keys, values) )
    
    # PRODUCT CATEGORY PROBABILITY
    values = df.iloc[6, 1:]
    data['PRODUCT CATEGORY PROBABILITY'] = dict( zip(keys, values) )
    
    # PROBABILITY OF HAVING BATTERY
    values = df.iloc[7, 1:]
    data['PROBABILITY OF HAVING BATTERY'] = dict( zip(keys, values) )
    
    # PROBABILITY OF HAVING CRT TUBE
    values = df.iloc[8, 1:]
    data['PROBABILITY OF HAVING CRT TUBE'] = dict( zip(keys, values) )

    # PROBABILITY OF HAVING CRT TUBE
    values = df.iloc[9, 1:]
    data['BATTERY PERCENTAGE OF PRODUCT MASS'] = dict( zip(keys, values) )

    # PROBABILITY OF HAVING CRT TUBE
    values = df.iloc[10, 1:]
    data['CRT TUBE PERCENTAGE OF PRODUCT MASS'] = dict( zip(keys, values) )  

    # CRT TUBE PROCESSING COST PER LB
    values = df.iloc[11, 1:]
    data['CRT TUBE PROCESSING COST PER LB'] = dict( zip(keys, values) )  
    
    # BATTERY PROCESSING COST PER LB
    values = df.iloc[11, 1:]
    data['BATTERY PROCESSING COST PER LB'] = dict( zip(keys, values) )
    
    return data

def read_material_movement_data(excel_file_name, sheet_name = 'Material Movement'):    
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name)
    dict_df = df.T.to_dict()
    data = [dict_df[key] for key in dict_df.keys()]
    # add TYPE to the dictionaries
    for idx, d in enumerate(data):
        d['TYPE'] = 'Material Handling Equipment'
        data[idx] = d
    
    return data

def read_storage_area_data(excel_file_name, sheet_name = 'Storage Areas'):    
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name)
    dict_df = df.T.to_dict()
    storage_area_data = [dict_df[key] for key in dict_df.keys()]
    
    return storage_area_data


def read_shredding_stations_data(excel_file_name, sheet_name = 'Shredding Work Stations'):
    df = pd.read_excel(io = excel_file_name, sheet_name = sheet_name)
    dict_df = df.T.to_dict()
    data = [dict_df[key] for key in dict_df.keys()]
    # add TYPE to the dictionaries
    for idx, d in enumerate(data):
        d['TYPE'] = 'Machine'
        data[idx] = d 
    
    return data 


def prepare_process_model_data(excel_file_name):
    process_model_data = []
    
    # read excel file
    xl = pd.ExcelFile(excel_file_name)
    # see all sheet names
    sheet_names = xl.sheet_names  
    manual_work_station_sheets  = []
    dismantling_station_sheets  = []
    product_source_sheets       = []
    
    for sheet in sheet_names:
        df = xl.parse(sheet_name = sheet, header = None)
        try:
            if df.iloc[0,1] == 'Manual Work Station':
                manual_work_station_sheets.append(sheet)
            elif df.iloc[0,1] == 'Dismantling Station':
                dismantling_station_sheets.append(sheet)
            elif df.iloc[0,1] == 'Product Source':
                product_source_sheets.append(sheet)
        except:
            pass
    
    try:
    #  append manual_work_station data    
        for sheet in manual_work_station_sheets:
            data = read_manual_work_station_data(excel_file_name = excel_file_name, sheet_name = sheet)
            process_model_data.append(data)
    except:
        pass
    
    try:
    #  append dismantling_stationn data    
        for sheet in dismantling_station_sheets:
            data = read_dismantling_station_data(excel_file_name = excel_file_name, sheet_name = sheet)
            process_model_data.append(data)
    except:
        pass
    
    try:
    #  append storage_area_data
        storage_area_data = read_storage_area_data(excel_file_name = excel_file_name)   
        for data in storage_area_data:
            process_model_data.append(data)
    except:
        pass
    
    # append shredding_stations_data
    try:
        shredding_stations_data = read_shredding_stations_data(excel_file_name)
        for data in shredding_stations_data:
            process_model_data.append(data)
    except:
        pass
        
    # append material movement data
    try:
        material_movement_data = read_material_movement_data(excel_file_name = excel_file_name)
        for data in material_movement_data:
            process_model_data.append(data)
    except:
        print('Error: Could not find material movement data')  
        
    # append product source data
    try:
        product_source_data = []
        for sheet in product_source_sheets:
            data = read_product_source_data(excel_file_name, sheet)
            product_source_data.append(data)
        for data in product_source_data:
            process_model_data.append(data)
    except:
        print('Error: Could not find product source data')  
        
    return process_model_data


class ContinuousStorage (simpy.Container):
    def __init__(self, env, name, capacity, init = 0, no_of_operators = 0, operator_wage_rate = 0):
        super().__init__(env, capacity, init)
        self.env                    = env      
        self.name                   = name
        self.no_of_operators        = no_of_operators  # operators required to run the machine
        self.operator_wage_rate     = operator_wage_rate   # $/hr
        self.cum_output             = 0
        self.capacity_utilization   = 0
        self.labor_cost             = 0.0
        self.total_input_lbs        = 0.0  # total amount of materials entered intot the storage
        self.item_wise_cost_per_lb  = [0] * len(categories)  
        self.summary_stats          = ''
        
        self.capacity_utilization_history               = []  # for time plot
        
        # call run method
        env.process( self.run() )
        
    def run(self):
        while True:
            yield self.env.timeout(1)  # delay 1 min to check stats
            self.cum_output += self.level
            self.capacity_utilization = self.cum_output / (self.env.now * self.capacity)
            self.labor_cost = self.no_of_operators * self.env.now * self.operator_wage_rate / 60 # 1/60: hr to min    
            self.capacity_utilization_history.append(self.level/self.capacity * 100)
            
    def create_summary_stats(self):
        # item_wise_cost_per_lb
        cost_per_lb = self.labor_cost / (self.total_input_lbs + 1e-10)  # 1e-10: to avoid zero division error
        self.item_wise_cost_per_lb  = [cost_per_lb] * len(categories) 
        
        # summary stats
        new_line = '\n'
        no_of_max_blank_space = len('Average capacity utilization')  # length of the longest text
        under_line = ( len(self.name) + len(' (storage area)') ) * '='
        
        self.summary_stats += f"{new_line}{self.name} (storage area){new_line}{under_line}{new_line}\
Current amount {(no_of_max_blank_space - len('Current amount') ) * ' '} : {self.level: ,.0f} lbs {new_line}\
Current capacity utilization {(no_of_max_blank_space - len('Current capacity utilization') ) * ' '} : {self.level/self.capacity * 100: ,.1f} % {new_line}\
Average capacity utilization {(no_of_max_blank_space - len('Average capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Entered material amount {(no_of_max_blank_space - len('Entered material amount') ) * ' '} : {self.total_input_lbs: ,.0f} lbs {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "


class UnitStorage (simpy.Store):
    def __init__(self, env, name, capacity, no_of_operators = 0, operator_wage_rate = 0):
        super().__init__(env, capacity)
        self.env                    = env      
        self.name                   = name
        self.no_of_operators        = no_of_operators  # operators required to run the machine
        self.operator_wage_rate     = operator_wage_rate   # $/hr
        self.cum_output             = 0
        self.capacity_utilization   = 0
        self.labor_cost             = 0.0
        self.total_input_lbs        = 0.0  # total amount of materials entered intot the storage
        self.input_mass_dist        = [0] * len(categories)  # distribution of materials entered into the storage
        self.item_wise_cost_per_lb  = [0] * len(categories)
        self.summary_stats          = ''
        
        self.capacity_utilization_history               = []  # for time plot
        
        # call run method
        env.process( self.run() )
        
    def run(self):
        while True:
            yield self.env.timeout(1)  # delay 1 min to check stats
            self.cum_output += len(self.items)
            self.capacity_utilization = self.cum_output / (self.env.now * self.capacity)  
            self.labor_cost = self.no_of_operators * self.env.now * self.operator_wage_rate / 60 # 1/60: hr to min 
            self.capacity_utilization_history.append(len(self.items)/self.capacity * 100)
            
    def create_summary_stats(self):
        # update self.total_input_lb
        self.total_input_lbs = sum(self.input_mass_dist)
        # calculate item_wise_cost_per_lb
        for idx, mass in enumerate(self.input_mass_dist):
            cost = self.labor_cost * mass / (sum(self.input_mass_dist) + 1e-10)  # 1e-10: to avoid zero division error
            self.item_wise_cost_per_lb[idx] = cost / (mass + + 1e-10)  # 1e-10: to avoid zero division error
        
        # summary stats
        new_line = '\n'
        no_of_max_blank_space = len('Average capacity utilization')  # length of the longest text
        under_line = ( len(self.name) + len(' (storage area)') ) * '='
        
        self.summary_stats += f"{new_line}{self.name} (storage area){new_line}{under_line} {new_line}\
Current amount {(no_of_max_blank_space - len('Current amount') ) * ' '} : {len(self.items): ,.0f} units {new_line}\
Current capacity utilization {(no_of_max_blank_space - len('Current capacity utilization') ) * ' '} : {len(self.items)/self.capacity * 100: ,.1f} % {new_line}\
Average capacity utilization {(no_of_max_blank_space - len('Average capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Entered material amount {(no_of_max_blank_space - len('Entered material amount') ) * ' '} : {self.total_input_lbs: ,.0f} lbs {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "




class Manual_work_station:  # a general class for manual work station, unit -> unit processing
    def __init__(self, env, data):        
        
        self.env                    = env        
        self.data                   = data
        self.name                   = data['NAME']
        self.operators              = simpy.Resource(env, data['NO OF OPERATORS'])
               
        self.busy_time              = 0.0
        self.capacity_utilization   = 0.0
        self.total_output_mass      = 0.0
        self.labor_cost             = 0.0
        
        self.output_mass_dist       = [0] * len(categories)  
        self.item_wise_time_dist    = [0] * len(categories)  # time spent in each categories   
        self.item_wise_cost_per_lb  = [0] * len(categories)  # time spent in each categories
        
        self.input_queue_lbs        = None  # placeholder
        self.output_queues_lbs      = {}    # dictionary
        self.input_queue_units      = None  # placeholder
        self.output_queues_units    = {}    # dictionary
        
        self.non_shreddable_output_dist = [0] * len(categories)  # lbs
        self.non_shreddable_output_total = 0.0                   # lbs      
                
        # text containing summary statistics
        self.summary_stats          = ''  # placeholder
        
        # store time dependent stats
        self.input_queue_capacity_utilization_history   = []
        self.capacity_utilization_history               = []   # total output capacity utilization
        
        ## call class method
        self.create_input_and_output_queues()
        
        ## call generators
        env.process(self.run())
        env.process(self.update_time_plot_stats())
        
        
        
    def create_input_and_output_queues(self):
        # input queue
        self.input_queue_lbs = ContinuousStorage(self.env, 
                                       name = f'{self.data["NAME"]} Input Queue', 
                                       capacity = self.data['INPUT QUEUE CAPACITY'])
        
        self.input_queue_units = UnitStorage(self.env, 
                                       name = f'{self.data["NAME"]} Input Queue', 
                                       capacity = 1e10)
        
        # output queues
        for idx, name in enumerate(self.data['OUTPUT QUEUE NAMES']):
            output_queue_lbs = ContinuousStorage(self.env, 
                                                 name = name, 
                                                 capacity = self.data['OUTPUT QUEUE CAPACITIES'][idx])
            
            output_queue_units = UnitStorage(self.env, 
                                             name = name, 
                                             capacity = 1e10)
            
            self.output_queues_lbs[name] = output_queue_lbs
            self.output_queues_units[name] = output_queue_units
        

    def run(self):
        while True:
                    
            if self.input_queue_lbs.level > 0: # item waiting in the queue
                req = self.operators.request()
                yield req
                self.env.process(self.do_processing(req)) 
                
            else: # no material waiting in the input queue
                yield self.env.timeout(1) # wait 1 min and check whether IF condition is true 
                
            
    def do_processing(self, req):
        ## get product from the input queue
        # in units
        product = yield self.input_queue_units.get() 
        # in lbs
        yield self.input_queue_lbs.get(product.mass)
        
        ## delay processing (sorting) time
        processing_time = self.data['PROCESSING TIME'][product.category]                          
        yield self.env.timeout(processing_time) 

        ## put product to the appropriate output queue
        queue_name = target_output_queue_name(self.data, product)
        
        # non_shreddable_mass
        if random.random() <= self.data['NON SHREDDABLE OUTPUT PROBABILITY'][product.category]:        
            non_shreddable_mass = self.data['NON SHREDDABLE OUTPUT PERCENTAGE'][product.category] * product.mass
        else:
            non_shreddable_mass = 0
            
        remaining_mass = product.mass - non_shreddable_mass
        # update product mass
        product.mass = remaining_mass
                
        yield self.output_queues_lbs[queue_name].put(product.mass) 
        yield self.output_queues_units[queue_name].put(product)              
        
        ## update stats
        self.non_shreddable_output_dist[dict_item_idx[product.category]] += non_shreddable_mass
        self.non_shreddable_output_total += non_shreddable_mass
        self.output_mass_dist[dict_item_idx[product.category]] += (non_shreddable_mass + remaining_mass)
        self.item_wise_time_dist[dict_item_idx[product.category]] += processing_time
        self.busy_time += processing_time
        self.total_output_mass += (non_shreddable_mass + remaining_mass)

        # release resource
        self.operators.release(req)
        
        
    def update_time_plot_stats(self):
        while True:
            yield self.env.timeout(1.0)  # update stats every minute
            
            self.capacity_utilization   = self.busy_time / (self.env.now * self.data['NO OF OPERATORS'] + 1e-10)
            self.labor_cost             = self.data['NO OF OPERATORS'] * self.env.now * self.data['OPERATOR WAGE RATE'] / 60 # 1/60: hr to min
            
            input_queue_capacity_utilization = self.input_queue_lbs.level / self.input_queue_lbs.capacity
            self.input_queue_capacity_utilization_history.append(input_queue_capacity_utilization) 
            self.capacity_utilization_history.append(self.capacity_utilization*100)
            
            
    def create_summary_stats(self):  # run this method after ending the simulation
        # calculate item_wise_cost_per_lb
        for idx, time in enumerate(self.item_wise_time_dist):
            cost = self.labor_cost * self.item_wise_time_dist[idx] / (sum(self.item_wise_time_dist) + 1e-10)  # 1e-10: to avoid zero division error  
            self.item_wise_cost_per_lb[idx] = cost / (self.output_mass_dist[idx] + self.non_shreddable_output_dist[idx] + 1e-10)  # 1e-10: to avoid zero division error  
        
        # generate text to show statistics
        new_line = '\n'
        no_of_max_blank_space = len('Total amount processed')  # length of the longest text
        
        self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Total amount processed {(no_of_max_blank_space - len('Total amount processed') ) * ' '} : {self.total_output_mass: ,.0f} lbs {new_line}\
Non-shreddable amount {(no_of_max_blank_space - len('Non-shreddable amount') ) * ' '} : {self.non_shreddable_output_total: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "



class Dismantling_station:  
    def __init__(self, env, data):        
        
        self.env                    = env        
        self.data                   = data
        self.name                   = data['NAME']
        self.operators              = simpy.Resource(env, data['NO OF OPERATORS'])
               
        self.busy_time              = 0.0
        self.capacity_utilization   = 0.0
        self.total_output_mass      = 0.0
        self.labor_cost             = 0.0
        
        self.output_mass_dist       = [0] * len(categories)  
        self.item_wise_time_dist    = [0] * len(categories)  # time spent in each categories 
        self.item_wise_cost_per_lb  = [0] * len(categories)
        
        self.input_queue_lbs        = None  # placeholder
        self.output_queue_lbs       = None  # placeholder
        self.input_queue_units      = None  # placeholder
        
        self.non_shreddable_output_dist = [0] * len(categories)  # lbs
        self.non_shreddable_output_total = 0.0                   # lbs      
                
        # text containing summary statistics
        self.summary_stats          = ''  # placeholder
        
        # store time dependent stats
        self.input_queue_capacity_utilization_history   = []
        self.capacity_utilization_history               = []   # total output capacity utilization
        
        ## call class method
        self.create_input_and_output_queues()
        
        ## call generators
        env.process(self.run())
        env.process(self.update_time_plot_stats())
        
        
        
    def create_input_and_output_queues(self):
        # input queue
        self.input_queue_lbs = ContinuousStorage(self.env, 
                                       name = f'{self.data["NAME"]} Input Queue', 
                                       capacity = self.data['INPUT QUEUE CAPACITY'])
        
        self.input_queue_units = UnitStorage(self.env, 
                                       name = f'{self.data["NAME"]} Input Queue', 
                                       capacity = 1e10)
        
        # output queue
        self.output_queue_lbs = ContinuousStorage(self.env, 
                                             name = f'{self.data["NAME"]} Output Queue', 
                                             capacity = self.data['OUTPUT QUEUE CAPACITY'])
        

    def run(self):
        while True:
                    
            if self.input_queue_lbs.level > 0: # item waiting in the queue
                req = self.operators.request()
                yield req
                self.env.process(self.do_processing(req)) 
                
            else: # no material waiting in the input queue
                yield self.env.timeout(1) # wait 1 min and check whether IF condition is true 
                
            
    def do_processing(self, req):
        ## get product from the input queue
        # in units
        product = yield self.input_queue_units.get() 
        # in lbs
        yield self.input_queue_lbs.get(product.mass)
        
        ## delay processing (sorting) time
        processing_time = self.data['PROCESSING TIME'][product.category]                          
        yield self.env.timeout(processing_time) 

        # non_shreddable_mass
        if random.random() <= self.data['NON SHREDDABLE OUTPUT PROBABILITY'][product.category]:        
            non_shreddable_mass = self.data['NON SHREDDABLE OUTPUT PERCENTAGE'][product.category] * product.mass
        else:
            non_shreddable_mass = 0
            
        remaining_mass = product.mass - non_shreddable_mass
        # update product mass
        product.mass = remaining_mass
        
        # put product to the output queue       
        yield self.output_queue_lbs.put(product.mass)             
        
        ## update stats
        self.non_shreddable_output_dist[dict_item_idx[product.category]] += non_shreddable_mass
        self.non_shreddable_output_total += non_shreddable_mass
        self.output_mass_dist[dict_item_idx[product.category]] += (non_shreddable_mass + remaining_mass)
        self.item_wise_time_dist[dict_item_idx[product.category]] += processing_time
        self.busy_time += processing_time
        self.total_output_mass += (non_shreddable_mass + remaining_mass)

        # release resource
        self.operators.release(req)
        
        
    def update_time_plot_stats(self):
        while True:
            yield self.env.timeout(1.0)  # update stats every minute
            
            self.capacity_utilization   = self.busy_time / (self.env.now * self.data['NO OF OPERATORS'] + 1e-10)
            self.labor_cost             = self.data['NO OF OPERATORS'] * self.env.now * self.data['OPERATOR WAGE RATE'] / 60 # 1/60: hr to min
            
            input_queue_capacity_utilization = self.input_queue_lbs.level / self.input_queue_lbs.capacity
            self.input_queue_capacity_utilization_history.append(input_queue_capacity_utilization) 
            self.capacity_utilization_history.append(self.capacity_utilization*100)
            
            
    def create_summary_stats(self):
        # calculate item_wise_cost_per_lb
        for idx, time in enumerate(self.item_wise_time_dist):
            cost = self.labor_cost * self.item_wise_time_dist[idx] / (sum(self.item_wise_time_dist) + 1e-10)  # 1e-10: to avoid zero division error  
            self.item_wise_cost_per_lb[idx] = cost / (self.output_mass_dist[idx] + self.non_shreddable_output_dist[idx] + 1e-10)  # 1e-10: to avoid zero division error 
        
        # generate text to show statistics
        new_line = '\n'
        no_of_max_blank_space = len('Total amount processed')  # length of the longest text
        
        self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Total amount processed {(no_of_max_blank_space - len('Total amount processed') ) * ' '} : {self.total_output_mass: ,.0f} lbs {new_line}\
Non-shreddable amount {(no_of_max_blank_space - len('Non-shreddable amount') ) * ' '} : {self.non_shreddable_output_total: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "



class Machine:  # in shredding station
    def __init__(self, env, data, energy_cost_per_kwh):
        
        # if a machine's input is directly connected to a conveyor, the input queue capacity = amount of materials conveyor can move in one minute
        # if a machine's output is directly connected to a conveyor, the output queue capacity = amount of materials conveyor can move in one minute
        self.env                    = env
        self.energy_cost_per_kwh    = energy_cost_per_kwh
        self.data                   = data
        self.name                   = data['NAME']  # name of the machine, i.e., 'shredder'
        self.input_queue_lbs        = simpy.Container(env, data['INPUT QUEUE CAPACITY'])
        self.output_queue_lbs       = simpy.Container(env, data['OUTPUT QUEUE CAPACITY']) 
        self.processing_capacity    = data['PROCESSING CAPACITY']  # processing capacity per minute
        self.cycle_time             = 1     # 1 min since capacity is defined in minute
        self.energy_consumption_rate = data['ENERGY CONSUMPTION RATE']   # in kWh
        self.no_of_operators        = data['NO OF OPERATORS']  # operators required to run the machine
        self.operator_wage_rate     = data['OPERATOR WAGE RATE']   # $/hr
        self.busy_time              = 0.0   # total busy time
        self.down_time              = 0.0        
        self.energy_consumption     = 0.0   # kWh        
        self.capacity_utilization   = 0.0   # in percentage
        self.idle_time_percentage   = 0.0     # idle time in percentage (0 to 1)                
        self.sorting_factor         = data['SORTING FACTOR']                      
        self.sorted_output = 0.0  # amount of sorted materials
        self.output                 = 0.0   # primary output 
        self.total_input_lbs        = 0.0 # total input materials entered into the machine
        self.total_output_mass      = 0
        
        self.labor_cost             = 0.0
        self.energy_cost            = 0.0
        
        self.item_wise_cost_per_lb  = [0] * len(categories)
        self.summary_stats          = ''  # text containing summary statistics
        self.capacity_utilization_history = [] # for time plot
        
        
        
        
        # call run_machine method
        env.process( self.run_machine() )
        
                     
    def run_machine(self):
        while True:
                    
            if self.input_queue_lbs.level > 0: # item waiting in the queue
                    
                material_amount = min(self.input_queue_lbs.level, self.processing_capacity)
                yield self.input_queue_lbs.get(material_amount)                    
                
                # delay processing time
                yield self.env.timeout(self.cycle_time)
                
                # put material to the output queue
                sorted_amount = material_amount * self.sorting_factor
                primary_output = material_amount - sorted_amount  # unsorted amount
                yield self.output_queue_lbs.put(primary_output)                    
                
                # update stats
                self.busy_time += self.cycle_time
                self.sorted_output += sorted_amount
                self.output += primary_output   # remaining amount after sorting 
                self.total_output_mass = self.sorted_output + self.output
                    
                
            else: # no material waiting in the input queue
                yield self.env.timeout(1) # wait 1 min and check whether IF condition is true                                
                
                
            # update stats irrespective of if & else condition                
            self.energy_consumption += self.energy_consumption_rate / 60  # 1/60: hr to min
            self.energy_cost        = self.energy_consumption * self.energy_cost_per_kwh
            self.capacity_utilization = (self.output + self.sorted_output) / (self.env.now * self.processing_capacity + 1e-10)
            self.idle_time_percentage = 1 - self.busy_time / (self.env.now + 1e-10)  # 1 - busy_time
            self.labor_cost = self.no_of_operators * self.env.now * self.operator_wage_rate / 60 # 1/60: hr to min
            self.capacity_utilization_history.append(self.capacity_utilization*100)
            

    def create_summary_stats(self):
        cost = self.labor_cost + self.energy_cost
        cost_per_lb = cost / (self.total_output_mass + 1e-10) # 1e-10: to avoid zero division error
        self.item_wise_cost_per_lb = [cost_per_lb] * len(categories)
        
        new_line = '\n'
        no_of_max_blank_space = len('Capacity utilization')  # length of the longest text
        
        # non-sorting machine
        if self.data['SORTING FACTOR'] == 0:        
            self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Primary output {(no_of_max_blank_space - len('Primary output') ) * ' '} : {self.output: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Idle time {(no_of_max_blank_space - len('Idle time') ) * ' '} : {self.idle_time_percentage * 100: ,.1f} % {new_line}\
Energy consumption {(no_of_max_blank_space - len('Energy consumption') ) * ' '} : {self.energy_consumption: ,.1f} kWh {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD " 
        
        # sorting machine
        elif self.data['ENERGY CONSUMPTION RATE'] > 0:        
            self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Primary output {(no_of_max_blank_space - len('Primary output') ) * ' '} : {self.output: ,.0f} lbs {new_line}\
Sorted materials {(no_of_max_blank_space - len('Sorted materials') ) * ' '} : {self.sorted_output: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Idle time {(no_of_max_blank_space - len('Idle time') ) * ' '} : {self.idle_time_percentage * 100: ,.1f} % {new_line}\
Energy consumption {(no_of_max_blank_space - len('Energy consumption') ) * ' '} : {self.energy_consumption: ,.1f} kWh {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "                 

        # manual sorting station
        else:        
            self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Primary output {(no_of_max_blank_space - len('Primary output') ) * ' '} : {self.output: ,.0f} lbs {new_line}\
Sorted materials {(no_of_max_blank_space - len('Sorted materials') ) * ' '} : {self.sorted_output: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % {new_line}\
Labor cost {(no_of_max_blank_space - len('Labor cost') ) * ' '} : {self.labor_cost: ,.0f} USD "              
                


class MaterialHandlingEquip:
    def __init__(self, env, name, moving_capacity, loading_point_station, unloading_point_station, loading_station_output_queue_name = None):
        self.env                                = env
        self.name                               = name
        self.loading_point_station              = loading_point_station
        self.loading_station_output_queue_name  = loading_station_output_queue_name
        self.unloading_point_station            = unloading_point_station
        self.moving_capacity                    = moving_capacity   # lbs/minute
        self.output                             = 0.0   # moved materials
        self.capacity_utilization               = 0.0   # in percentage
        
        self.type                               = None  # potential types are given below  
        # manual_work_station_TO_manual_work_station, manual_work_station_TO_dismantling_station
        # manual_work_station_TO_unit_storage  
        # dismantling_station_TO_continuous_storage, any_shredding_machine_TO_continuous_storage
        # unit_storage_TO_dismantling_station,  unit_storage_TO_manual_work_station 
        # unit_storage_TO_unit_storage 
        # manual_work_station_TO_continuous_storage        
        # continuous_storage_TO_any_shredding_machine 
        # any_shredding_machine_TO_any_shredding_machine, dismantling_station_TO_any_shredding_machine
        # unit_storage_TO_continuous_storage

        # text containing summary statistics
        self.summary_stats = ''  # placeholder        
        
        # call set_attributes method
        self.set_attributes()
        
        # call run method
        env.process( self.run() )
        
    def set_attributes(self):
        if isinstance(self.loading_point_station, Manual_work_station) and isinstance(self.unloading_point_station, Manual_work_station):
            self.type = 'manual_work_station_TO_manual_work_station'
            
        elif isinstance(self.loading_point_station, Manual_work_station) and isinstance(self.unloading_point_station, Dismantling_station):
            self.type = 'manual_work_station_TO_dismantling_station'
        
        elif isinstance(self.loading_point_station, Manual_work_station) and isinstance(self.unloading_point_station, UnitStorage):
            self.type = 'manual_work_station_TO_unit_storage'
            
        elif isinstance(self.loading_point_station, Dismantling_station) and isinstance(self.unloading_point_station, ContinuousStorage):
            self.type = 'dismantling_station_TO_continuous_storage'    
            
        elif isinstance(self.loading_point_station, UnitStorage) and isinstance(self.unloading_point_station, Dismantling_station):
            self.type = 'unit_storage_TO_dismantling_station'     
            
        elif isinstance(self.loading_point_station, UnitStorage) and isinstance(self.unloading_point_station, Manual_work_station):
            self.type = 'unit_storage_TO_manual_work_station'  
        
        elif isinstance(self.loading_point_station, UnitStorage) and isinstance(self.unloading_point_station, UnitStorage):
            self.type = 'unit_storage_TO_unit_storage'
        
        elif isinstance(self.loading_point_station, Manual_work_station) and isinstance(self.unloading_point_station, ContinuousStorage):
            self.type = 'manual_work_station_TO_continuous_storage'
            
        elif isinstance(self.loading_point_station, Machine) and isinstance(self.unloading_point_station, ContinuousStorage):
            self.type = 'any_shredding_machine_TO_continuous_storage'
            
        elif isinstance(self.loading_point_station, ContinuousStorage) and isinstance(self.unloading_point_station, Machine):
            self.type = 'continuous_storage_TO_any_shredding_machine'        
        
        elif isinstance(self.loading_point_station, Machine) and isinstance(self.unloading_point_station, Machine):
            self.type = 'any_shredding_machine_TO_any_shredding_machine' 
        
        elif isinstance(self.loading_point_station, Dismantling_station) and isinstance(self.unloading_point_station, Machine):
            self.type = 'dismantling_station_TO_any_shredding_machine'
        
        elif isinstance(self.loading_point_station, UnitStorage) and isinstance(self.unloading_point_station, ContinuousStorage):
            self.type = 'unit_storage_TO_continuous_storage'
        
        else:
            print(f'Error in MaterialHandlingEquip: {self.name}. Self.type attribute could not be determined')
            
            
            
        if self.type in ['manual_work_station_TO_manual_work_station', 'manual_work_station_TO_dismantling_station']:
            self.loading_point_units    = self.loading_point_station.output_queues_units[self.loading_station_output_queue_name]
            self.loading_point_lbs      = self.loading_point_station.output_queues_lbs[self.loading_station_output_queue_name]
            self.unloading_point_units  = self.unloading_point_station.input_queue_units
            self.unloading_point_lbs    = self.unloading_point_station.input_queue_lbs            
            
        elif self.type in ['manual_work_station_TO_unit_storage']:
            self.loading_point_units    = self.loading_point_station.output_queues_units[self.loading_station_output_queue_name]
            self.loading_point_lbs      = self.loading_point_station.output_queues_lbs[self.loading_station_output_queue_name]
            self.unloading_point_units  = self.unloading_point_station
   
        elif self.type in ['dismantling_station_TO_continuous_storage', 'any_shredding_machine_TO_continuous_storage']:
            self.loading_point_lbs      = self.loading_point_station.output_queue_lbs
            self.unloading_point_lbs    = self.unloading_point_station
            
        elif self.type in ['unit_storage_TO_dismantling_station',  'unit_storage_TO_manual_work_station']:
            self.loading_point_units    = self.loading_point_station
            self.unloading_point_units  = self.unloading_point_station.input_queue_units
            self.unloading_point_lbs    = self.unloading_point_station.input_queue_lbs          
        
        elif self.type in ['unit_storage_TO_unit_storage']:
            self.loading_point_units    = self.loading_point_station
            self.unloading_point_units  = self.unloading_point_station
        
        elif self.type in ['manual_work_station_TO_continuous_storage']:
            self.loading_point_units    = self.loading_point_station.output_queues_units[self.loading_station_output_queue_name]
            self.loading_point_lbs      = self.loading_point_station.output_queues_lbs[self.loading_station_output_queue_name]
            self.unloading_point_lbs    = self.unloading_point_station
        
        elif self.type in ['continuous_storage_TO_any_shredding_machine']:
            self.loading_point_lbs      = self.loading_point_station
            self.unloading_point_lbs    = self.unloading_point_station.input_queue_lbs    
        
        elif self.type in ['any_shredding_machine_TO_any_shredding_machine', 'dismantling_station_TO_any_shredding_machine']:
            self.loading_point_lbs      = self.loading_point_station.output_queue_lbs
            self.unloading_point_lbs    = self.unloading_point_station.input_queue_lbs
            
        elif self.type in ['unit_storage_TO_continuous_storage']:
            self.loading_point_units    = self.loading_point_station
            self.unloading_point_lbs    = self.unloading_point_station
            
    
    def run(self):
        while True:
            #---------------------------------------------------------------------------------
            if self.type in ['manual_work_station_TO_manual_work_station', 'manual_work_station_TO_dismantling_station']:
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        yield self.loading_point_lbs.get(item.mass)
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_lbs.put(item.mass)
                        yield self.unloading_point_units.put(item)
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
            
            #---------------------------------------------------------------------------------
            elif self.type in ['manual_work_station_TO_unit_storage']:
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        yield self.loading_point_lbs.get(item.mass)
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_units.put(item)
                        # update self.input_mass_dist
                        self.unloading_point_units.input_mass_dist[dict_item_idx[item.category]] += item.mass
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)


            #---------------------------------------------------------------------------------
            elif self.type in ['dismantling_station_TO_continuous_storage', 
                               'any_shredding_machine_TO_continuous_storage', 
                               'continuous_storage_TO_any_shredding_machine',
                               'any_shredding_machine_TO_any_shredding_machine', 
                               'dismantling_station_TO_any_shredding_machine']:
                if self.loading_point_lbs.level > 0: # item waiting in the loading_point
                
                    collected_mass = min(self.loading_point_lbs.level, self.moving_capacity)
                    # load pallet                    
                    yield self.loading_point_lbs.get(collected_mass)
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    # if (self.unloading_point_lbs.capacity - self.unloading_point_lbs.level) < collected_mass:
                    #     print(f'Error: Not enough available space at {self.name} for the arriving materials to unload')
                    yield self.unloading_point_lbs.put(collected_mass)
                    # update self.total_input_lbs
                    if isinstance(self.unloading_point_lbs, ContinuousStorage):
                        self.unloading_point_lbs.total_input_lbs += collected_mass
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)


            #---------------------------------------------------------------------------------
            elif self.type in ['unit_storage_TO_dismantling_station',  'unit_storage_TO_manual_work_station']:
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_lbs.put(item.mass)
                        yield self.unloading_point_units.put(item)
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)

            #---------------------------------------------------------------------------------
            elif self.type in ['unit_storage_TO_unit_storage']:
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_units.put(item)
                        # update self.input_mass_dist
                        self.unloading_point_units.input_mass_dist[dict_item_idx[item.category]] += item.mass
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
            #---------------------------------------------------------------------------------
            elif self.type in ['manual_work_station_TO_continuous_storage']:
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        yield self.loading_point_lbs.get(item.mass)
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_lbs.put(item.mass)
                        # update self.total_input_lbs
                        self.unloading_point_lbs.total_input_lbs += item.mass
                        
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)        

            #---------------------------------------------------------------------------------
            elif self.type in ['unit_storage_TO_continuous_storage']:
                
                if len(self.loading_point_units.items) > 0: # item waiting in the loading_point
                    pallet = []
                    collected_mass = 0    
                    # load pallet with items until moving_capacity
                    for item in self.loading_point_units.items:
                        item = yield self.loading_point_units.get()
                        pallet.append(item) 
                        collected_mass += item.mass
                        if collected_mass >= self.moving_capacity:
                            break
                    
                    # delay 1 min
                    yield self.env.timeout(1.0)
                    
                    # unload pallet at the unloading_point
                    for item in pallet:
                        yield self.unloading_point_lbs.put(item.mass)
                        # update self.total_input_lbs
                        self.unloading_point_lbs.total_input_lbs += item.mass
                    
                    # update stats
                    self.output += collected_mass
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)
                    
                else: # there is no item waiting
                    yield self.env.timeout(1.0)
                    # update stats
                    self.capacity_utilization = self.output / (self.env.now * self.moving_capacity + 1e-10)


    def create_summary_stats(self):
        new_line = '\n'
        no_of_max_blank_space = len('Material amount moved')  # length of the longest text
        
        self.summary_stats += f"{new_line}{self.name}{new_line}{ len(self.name) * '=' }{new_line}\
Material amount moved {(no_of_max_blank_space - len('Material amount moved') ) * ' '} : {self.output: ,.0f} lbs {new_line}\
Capacity utilization {(no_of_max_blank_space - len('Capacity utilization') ) * ' '} : {self.capacity_utilization * 100: ,.1f} % "


                    

class Product:
    def __init__(self, source, data):
        self.d                          = data           
        self.source                     = source  # business or residential
        self.category                   = None    # placeholder        
        self.mass                       = None    # placeholder 
        self.has_battery                = False
        self.has_crt_tube               = False
        self.battery_mass               = 0.0    # lb
        self.crt_tube_mass              = 0.0    # lb
        
        self.set_product_attributes()  # call this class method to set product attributes

    
    def set_product_attributes(self):
        
        ## determine product category
        # generate a random number
        x = random.random()
        
        # list of keys or products
        keys = list( self.d['PRODUCT CATEGORY PROBABILITY'].keys() )

        cum_prob = 0
        for key in keys:
            cum_prob += self.d['PRODUCT CATEGORY PROBABILITY'][key]
            if x <= cum_prob:
                self.category = key
                break

        ## product mass
        self.mass = self.d['PRODUCT MASS'][self.category]
        
        ## has_battery attribute and battery_mass
        if random.random() <= self.d['PROBABILITY OF HAVING BATTERY'][self.category]:
            self.has_battery = True
            self.battery_mass = self.mass * self.d['BATTERY PERCENTAGE OF PRODUCT MASS'][self.category]

        ## crt_tube_mass
        if random.random() <= self.d['PROBABILITY OF HAVING CRT TUBE'][self.category]:
            self.has_crt_tube = True
            self.crt_tube_mass = self.mass * self.d['CRT TUBE PERCENTAGE OF PRODUCT MASS'][self.category]
        





def show_progress(ws):
    while True:
        progress_bar(total_iteration = ws.sim_time, current_iteration = ws.env.now + 1)
        yield ws.env.timeout(1) 


#===========================================================================================


categories = ['crt_tv', 'crt_monitor', 'lcd_tv', 'lcd_monitor', 'desktop', 'laptop', 'printer', 'small_cee', 'peripherals']
position_idx = range(len(categories))  # position of the keys in the list
dict_item_idx = dict(zip(categories, position_idx))   # retun the position index of the items (keys)

# simulation time period
class SimTimeData:
    weeks                       = 1
    days                        = 5
    shifts                      = 1
    hours                       = 8
    sim_time                    = weeks * days * shifts * hours * 60    # simulation time in minutes
    energy_cost_per_kwh         = 0.11
    

class Warehouse_simulation:
    def __init__(self, process_model_data, sim_time_data):
        self.process_model_data             = process_model_data
        self.sim_time_data                  = sim_time_data
        self.env                            = simpy.Environment()
        self.sim_time                       = sim_time_data.sim_time
        self.energy_cost_per_kwh            = sim_time_data.energy_cost_per_kwh

        self.overall_input_mass_dist        = [0] * len(categories)
        self.crt_tube_mass_dist             = [0] * len(categories)
        self.battery_mass_dist              = [0] * len(categories)
        
        self.crt_tube_treatment_cost_dist   = [0] * len(categories)
        self.battery_treatment_cost_dist    = [0] * len(categories)
        
        self.processes                      = []  # this list includes: 'Manual Work Station', 'Dismantling Station', and 'Storage Areas'
        self.material_movement_processes    = []
        
        self.item_wise_processing_cost_per_lb = [0] * len(categories)
        
        self.text                               = ''  # text containing summary_stats




    def generate_product(self, env, target_station, data):
        source = data['NAME']
        product_created_lbs = 0
        while True:        
            product = Product(source, data)
            if isinstance(target_station, Manual_work_station) or isinstance(target_station, Dismantling_station):
                yield target_station.input_queue_lbs.put(product.mass) 
                target_station.input_queue_units.put(product)  
            
            elif isinstance(target_station, UnitStorage):
                yield target_station.put(product) 
                # update self.input_mass_dist
                target_station.input_mass_dist[dict_item_idx[product.category]] += product.mass
            
            elif isinstance(target_station, ContinuousStorage):
                yield target_station.put(product.mass)
                # update self.total_input_lbs
                target_station.total_input_lbs += product.mass
    
            # update stats
            self.overall_input_mass_dist[dict_item_idx[product.category]]        += product.mass
            self.crt_tube_mass_dist[dict_item_idx[product.category]]             += product.crt_tube_mass
            self.battery_mass_dist[dict_item_idx[product.category]]              += product.battery_mass
            self.crt_tube_treatment_cost_dist[dict_item_idx[product.category]]   += product.crt_tube_mass * data['CRT TUBE PROCESSING COST PER LB'][product.category]
            self.battery_treatment_cost_dist[dict_item_idx[product.category]]    += product.battery_mass * data['BATTERY PROCESSING COST PER LB'][product.category]
            product_created_lbs += product.mass
            
            if product_created_lbs > data['PRODUCT AMOUNT']:
                break


    def system_builder(self, env, process_model_data):
        ## create 'Manual Work Station', 'Dismantling Station', and 'Storage Areas'
        for data in process_model_data:
            if data['TYPE'] == 'Manual Work Station':
                process = Manual_work_station(env, data)
                self.processes.append(process)
            
            elif data['TYPE'] == 'Dismantling Station':
                process = Dismantling_station(env, data)
                self.processes.append(process)
                
            elif data['TYPE'] == 'Unit Storage':
                process = UnitStorage(env, 
                                      name = data['NAME'], 
                                      capacity = data['STORAGE CAPACITY'],
                                      no_of_operators = data['NO OF OPERATORS'], 
                                      operator_wage_rate = data['OPERATOR WAGE RATE'])
                
                self.processes.append(process)
            
            elif data['TYPE'] == 'Continuous Storage':
                process = ContinuousStorage(  env, 
                                              name = data['NAME'], 
                                              capacity = data['STORAGE CAPACITY'],
                                              no_of_operators = data['NO OF OPERATORS'], 
                                              operator_wage_rate = data['OPERATOR WAGE RATE'])
                
                self.processes.append(process)
        
            elif data['TYPE'] == 'Machine':
                process = Machine(env, data, self.energy_cost_per_kwh)        
                self.processes.append(process)
        
        ## generate products
        for data in process_model_data:
            if data['TYPE'] == 'Product Source':
                target_station_name = data['INITIAL LOCATION']
                
                # find the target_station from name
                for p in self.processes:
                    if p.name == target_station_name:
                        target_station = p
                        break
                # generate product at the target station
                env.process(self.generate_product(env, target_station, data))
        
        
        
        ## create material movement processes        
        for d in process_model_data:
            if d['TYPE'] == 'Material Handling Equipment':
                name = d['NAME']
                loading_point_station_name = d['LOADING STATION NAME']
                loading_station_output_queue_name = d['LOADING STATION OUTPUT QUEUE NAME']
                unloading_point_station_name = d['UNLOADING STATION NAME']
                moving_capacity = d['MOVING CAPACITY']
                
                # find loading_point_station from name
                for p in self.processes:
                    if p.name == loading_point_station_name:
                        loading_point_station = p
                        break
            
                # find unloading_point_station from name
                for p in self.processes:
                    if p.name == unloading_point_station_name:
                        unloading_point_station = p
                        break   
               
                process = MaterialHandlingEquip(env, 
                                                name, 
                                                moving_capacity, 
                                                loading_point_station, 
                                                unloading_point_station, 
                                                loading_station_output_queue_name)
                self.material_movement_processes.append(process)
    


    def calculate_per_lb_cost(self):
        for p in self.processes:
            # run create_summary_stats() method to create item_wise_cost_per_lb attribute
            p.create_summary_stats()
            # add two lists: item_wise_cost_per_lb and p.item_wise_cost_per_lb
            self.item_wise_processing_cost_per_lb = [x + y for x, y in zip(self.item_wise_processing_cost_per_lb, p.item_wise_cost_per_lb)]
    

    def add_crt_and_battery_treatment_cost_to_per_lb_cost(self):
        updated_item_wise_cost_per_lb = self.item_wise_processing_cost_per_lb.copy()
        for idx, cost in enumerate(self.item_wise_processing_cost_per_lb):
            # crt treatment cost
            crt_cost_per_lb = self.crt_tube_treatment_cost_dist[idx] / (self.overall_input_mass_dist[idx] + 1e-10)  # 1e-10: to avoid zero division error
            updated_item_wise_cost_per_lb[idx] += crt_cost_per_lb
            
            # battery treatment cost
            battery_cost_per_lb = self.battery_treatment_cost_dist[idx] / (self.overall_input_mass_dist[idx] + 1e-10)  # 1e-10: to avoid zero division error
            updated_item_wise_cost_per_lb[idx] += battery_cost_per_lb
            
        self.item_wise_processing_cost_per_lb = updated_item_wise_cost_per_lb
        
 
    def export_result(self):
        # target data
        amount_lb_per_month = np.array(self.overall_input_mass_dist) * 4.33333 / self.sim_time_data.weeks
        data = [categories,
                amount_lb_per_month,
                self.item_wise_processing_cost_per_lb]
        
        # create data frame
        df = pd.DataFrame(data).transpose()
      
        # column names
        df.columns = ['item', 'amount_lb_per_month', 'processing_cost_per_lb_without_overhead' ]
 
        # export to a csv file
        file_name = 'process_simulation_output.csv'
        # self.df_stats.to_csv(file_name, sep=',', encoding='utf-8', index=False)
        with open(file_name, 'w') as f:           # Drop to csv w/ context manager
            df.to_csv(f, sep=',', index=False, encoding='utf-8', line_terminator='\n') 
            
            
    def run_simulation(self):
        try:
            self.system_builder(self.env, self.process_model_data)      
            
            # show simulation progress bar on console
            self.env.process(show_progress(self))
            
            # run simulation
            self.env.run(until = self.sim_time)
            
            self.calculate_per_lb_cost()        
            self.add_crt_and_battery_treatment_cost_to_per_lb_cost()
            
            # add summary stats to the self.text attribute
            for p in self.processes:
                self.text += p.summary_stats + '\n'
                
            # export results to csv file
            self.export_result()
        
        except Exception as e: 
            self.text = f'{type(e).__name__}: {e.args}'


if __name__ == "__main__":
    # reproduce the results
    random.seed(42)
    excel_file_name = 'TEMPLATE_process_model_data_sample.xlsx'
    # get process model data from excel file
    process_model_data = prepare_process_model_data(excel_file_name)
    sim_time_data = SimTimeData()
    ws = Warehouse_simulation(process_model_data, sim_time_data)
    ws.run_simulation()
    print(ws.text)




   
