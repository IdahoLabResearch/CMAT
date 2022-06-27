"""
@author: Mamunur Rahman
"""


import numpy as np


## define some functions
# returns sum of flows
def flowSum(flow):
    '''
    example
    ----------
    f1 = [1, 2, 3]
    f2 = [4, 5, 6]
    flowSum([f1, f2])

    Returns
    -------
    [5, 7, 9]

    '''
    value = np.array(flow).sum(axis = 0)
    value = value.round(4)
    value = value.tolist()
    return value


# returns product of flows
def flowProduct( python_list ):
    '''
    example
    ----------
    a = [1, 2, 3]
    b = [1, 2, 3]
    c = [1, 0.5, 0.1]
    flowProduct([a, b, c])

    Returns
    -------
    [1.0, 2.0, 0.9]

    '''
    array = []
    for x in python_list:
        array.append(np.array(x))
    product = np.prod(np.vstack(array), axis=0)
    product = product.round(4)
    product = list(product)
    return product


def flowDivide(a, b):
    '''
    example
    ----------
    a = [1, 2, 3]
    b = [1, 2, .5]
    flowDivide(a, b)

    Returns
    -------
    [1, 1, 6]

    '''
    # convert number --> list
    if type(a) != list:
        a = [a]
    if type(b) != list:
        b = [b]
    
    # match the length of both list
    if len(a) > len(b):
        b = b*len(a)
    if len(a) < len(b):
        a = a*len(b)
    
    a = np.array(a)
    b = np.array(b)
    value = a/b
    value = value.round(4)
    value = value.tolist()
    return value


def flowSubtract(a, b):
    '''
    example
    ----------
    a = [1, 2, 3]
    b = [1, 2, .5]
    flowSubtract(a, b)

    Returns
    -------
    [0, 0, 2.5]

    '''
    # convert number --> list
    if type(a) != list:
        a = [a]
    if type(b) != list:
        b = [b]
    
    # match the length of both list
    if len(a) > len(b):
        b = b*len(a)
    if len(a) < len(b):
        a = a*len(b)
    
    a = np.array(a)
    b = np.array(b)
    value = a - b
    value = value.round(4)
    value = value.tolist()
    return value


# returns a list of flow by multiplying flows and corresponding factors
def flowAndfactor(flows, factors):
    '''
    example
    ----------
    flows = [[1, 2, 3], [4, 5, 6]]
    factors = [0.5, 0.5, 0.5], [0.1, 0.1, 0.1]
    flowAndfactor(flows, factors)
    
    Returns
    -------
    [[0.5, 1.0, 1.5], [0.4, 0.5, 0.6]]

    '''
    flows = np.array(flows)
    factors = np.array(factors)
    z = (flows * factors)
    z = z.round(4)
    z = z.tolist()
    return z


# dissolve subscripts
def dissolveSubs(flows):
    '''
    example
    ----------
    flows = [1, 2, 3]
    dissolveSubs(flows)

    Returns
    -------
    6

    '''
    value = sum(flows)
    return value

# returns the dimension of a python list
def dim(a):
    b = np.array(a)
    if b.size == 0:
        dimension = 0
    else:
        dimension = len( b.shape )
    return  dimension


type([1.0]) != list

#%%
## define Revenue class
class Revenue:
    def __init__(self, material_amount, per_unit_price):
        if type(per_unit_price) != list:
            self.per_unit_price = [per_unit_price]
        else:
           self.per_unit_price = per_unit_price 
           
        self.material_amount = material_amount
        self.revenue = self.calculate_revenue()
        
        
    def calculate_revenue(self):
        if dim(self.material_amount) == 1:
            sum_input_materials = self.material_amount
        else:
            sum_input_materials = flowSum(self.material_amount) # make a single list by summing up
        
        length_sum_input_materials = len(sum_input_materials) # list length --> number of eWaste categories in the subscript        
        length_per_unit_price = len(self.per_unit_price)
        
        if length_per_unit_price != length_sum_input_materials:
            formatted_per_unit_price = self.per_unit_price * length_sum_input_materials
        else:
            formatted_per_unit_price = self.per_unit_price
        
        #calculate revenue
        revenue = flowAndfactor(sum_input_materials, formatted_per_unit_price)
        
        return revenue
        
            

#%%
## define Stock class
class Stock:
    def __init__(self, inflow = [], outflow = [], initial_stock = [], **kwargs):
        
        ## inflow------------------------------
        if dim(inflow) == 0:
            print('Error: Inflow is missing')
        
        elif dim(inflow) == 1 and 'inflow_factors' not in kwargs:
            self.inflow = inflow
            self.inflow_sum = inflow
            
        elif dim(inflow) == 1 and 'inflow_factors' in kwargs:
            flows = inflow
            factors = kwargs['inflow_factors']
            self.inflow = flowAndfactor(flows, factors)
            self.inflow_sum = self.inflow
        
        elif dim(inflow) == 2 and 'inflow_factors' not in kwargs:
            self.inflow = inflow
            self.inflow_sum = flowSum(inflow)
            
        elif dim(inflow) == 2 and 'inflow_factors' in kwargs:
            flows = inflow
            factors = kwargs['inflow_factors']
            self.inflow = flowAndfactor(flows, factors)
            self.inflow_sum = flowSum(self.inflow)
        
        else:
            print('Error: Only 1D or 2D list are supported')
                    
            
        ## initial stock--------------------------------------
        if dim(initial_stock) == 0:
            self.initial_stock = [0]*len(self.inflow_sum)
        elif dim(initial_stock) == 1:
            self.initial_stock = initial_stock
        else:
            print('Error: Only 1D lists are supported')   
        
        ## outflow----------------------------------------------
        if dim(outflow) == 1 and 'outflow_factors' not in kwargs:
            self.outflow = outflow
            self.outflow_sum = outflow
        
        elif dim(outflow) == 1 and 'outflow_factors' in kwargs:
            flows = outflow
            factors = kwargs['outflow_factors']
            self.outflow = flowAndfactor(flows, factors)
            self.outflow_sum = self.outflow
        
        elif dim(outflow) == 2 and 'outflow_factors' not in kwargs:
            self.outflow = outflow
            outflow_sum = flowSum(outflow)
            self.outflow_sum = outflow_sum
        
        elif dim(outflow) == 2 and 'outflow_factors' in kwargs:
            flows = outflow
            factors = kwargs['outflow_factors']
            self.outflow = flowAndfactor(flows, factors)
            self.outflow_sum = flowSum(self.outflow)
            
            
        elif dim(outflow) == 0 and 'outflow_factors' in kwargs:  # if only 'outflow_factors' exists, current stock value will be used
            
            factors = kwargs['outflow_factors']
            stock_ = np.array(self.inflow_sum) + np.array(self.initial_stock)  # numpy array
            stock_ = stock_.tolist() # python 1D list
            
            if dim(factors) == 1:
                flows = flowAndfactor(stock_, factors)
                self.outflow = flows
                self.outflow_sum = flows
                
            elif dim(factors) == 2:
                stock_formatted = []            
                for _ in factors:
                    stock_formatted.append(stock_)

                flows = flowAndfactor(stock_formatted, factors)
                self.outflow = flows
                self.outflow_sum = flowSum(self.outflow)
            else:
                print('Error: Only 1D or 2D list are supported')
                                 
        
        else:
           print('Error: Only 1D or 2D list are supported') 
        
        ## current stock--------------------------------------
        self.current_stock = self.currentStock()
      
    def currentStock(self):
        stock = []
        for a, b, c in zip(self.initial_stock, self.inflow_sum, self.outflow_sum):
            value = max( (a + b - c), 0 ) # ensures stock is not negative
            stock.append(value)
        return stock
    

    
    
if __name__ == '__main__':    
    
    ## Stock class
    s1 = Stock(inflow = [20, 30], initial_stock = [10, 10], outflow_factors = [0.1, 0.1])
    print( s1.inflow )
    print( s1.initial_stock )
    print( s1.outflow )
    print( s1.current_stock )
    
    print()
    s2 = Stock(inflow = [20, 30], initial_stock = [0, 0], outflow = [10, 10])
    print( s2.inflow )
    print( s2.initial_stock )
    print( s2.outflow )
    print( s2.current_stock )
    
    print()
    s3 = Stock(inflow = [[20, 30], [20, 30]], initial_stock = [0, 0], outflow = [[10, 10], [10, 10]])
    print( s3.inflow )
    print( s3.inflow_sum )
    print( s3.initial_stock )
    print( s3.outflow )
    print( s3.outflow_sum )
    print( s3.current_stock )

    print()
    s4 = Stock(inflow = [[20, 30], [20, 30]], initial_stock = [0, 0], outflow_factors = [[.1, .1], [.5, .5]])
    print( s4.inflow )
    print( s4.inflow_sum )
    print( s4.initial_stock )
    print( s4.outflow )
    print( s4.outflow_sum )
    print( s4.current_stock )
    
    print()
    s5 = Stock(inflow = [20, 30], initial_stock = [0, 0], outflow = [10, 10], outflow_factors = [.1, .1])
    print( s5.inflow )
    print( s5.inflow_sum )
    print( s5.initial_stock )
    print( s5.outflow )
    print( s5.outflow_sum )
    print( s5.current_stock )
    
    print()
    s6 = Stock(inflow = [[20, 30], [20, 30]], initial_stock = [0, 0], outflow = [[10, 10], [20, 20]], outflow_factors = [[.1, .1], [.5, .5]])
    print( s6.inflow )
    print( s6.inflow_sum )
    print( s6.initial_stock )
    print( s6.outflow )
    print( s6.outflow_sum )
    print( s6.current_stock )
    
    print()
    s7 = Stock(inflow = [20, 30], initial_stock = [0, 0], outflow = [10, 10], inflow_factors = [.1, .1])
    print( s7.inflow )
    print( s7.inflow_sum )
    print( s7.initial_stock )
    print( s7.outflow )
    print( s7.outflow_sum )
    print( s7.current_stock )
    
    print()
    s7 = Stock(inflow = [[20, 30], [20, 30]], initial_stock = [50, 50], outflow = [[10, 10], [20, 20]], inflow_factors = [[.1, .1], [.5, .5]])
    print( s7.inflow )
    print( s7.inflow_sum )
    print( s7.initial_stock )
    print( s7.outflow )
    print( s7.outflow_sum )
    print( s7.current_stock )
    
    print()
    s8 = Stock(inflow = [[20, 30], [20, 30]], initial_stock = [50, 50], outflow = [[10, 10], [20, 20]], inflow_factors = [[.1, .1], [.5, .5]], outflow_factors = [[.1, .1], [.5, .5]])
    print( s8.inflow )
    print( s8.inflow_sum )
    print( s8.initial_stock )
    print( s8.outflow )
    print( s8.outflow_sum )
    print( s8.current_stock )
    print()
    
    ## revenue class
    r1 = Revenue(material_amount = [1, 2, 3], per_unit_price=.1)
    print(f'Revenue: {r1.revenue}')
    
    r1 = Revenue(material_amount = [1, 2, 3], per_unit_price=[.1])
    print(f'Revenue: {r1.revenue}')
    
    r2 = Revenue(material_amount = [1, 2, 3], per_unit_price=[.1, 0, .5])
    print(f'Revenue: {r2.revenue}')
    
    r3 = Revenue(material_amount = [ [1, 2, 3], [1, 2, 3] ], per_unit_price=[.1, 0, .5])
    print(f'Revenue: {r3.revenue}')



 
    
    
    
    
    
    
    
    
    
    
    