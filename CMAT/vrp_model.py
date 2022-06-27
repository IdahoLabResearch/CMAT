"""
@author: Mamunur Rahman
"""

import numpy as np
import pandas as pd
import folium
from folium.plugins import AntPath


class Node:
    def __init__(self):
        self.id             = 0
        self.account_id     = 0
        self.account_name   = ''
        self.address        = ''
        self.lat            = 0.0
        self.lon            = 0.0
        self.amount         = 0.0
        self.depot          = False  # base depot?
        self.not_visited    = True  # if any vehicle already visited this node or not


class Truck:
    def __init__(self):
        self.id                     = 0
        self.name                   = ''
        self.capacity               = 0
        self.mass                   = 0.0  # kg
        self.engine_displacement    = 0.0
        self.frontal_area           = 5.5
        self.mu_rr                  = 0.07
        self.air_density            = 1.18
        self.c_d                    = 0.8
        self.engine_efficiency      = 0.45
        self.idle_engine_rpm        = 600
        self.max_engine_rpm         = 2200
        self.engine_friction_factor = 0.25
        self.drive_train_efficiency = 0.8
        self.fuel_air_mass_ratio    = 1/14.5
        self.fuel_calorific_value   = 45.5
        self.fuel_density           = 0.846
        self.visited_nodes          = []  # list of visited nodes
        self.remaining_capacity     = 0   
        


class VRP:
    def __init__(self, df_vehicles, df_od_matrix, df_collection_points, df_unique_addresses, obj = 'distance', weight_per_pallet_lbs = 500):

        self.df_vehicles            = df_vehicles
        self.df_collection_points   = df_collection_points
        self.df_unique_addresses    = df_unique_addresses
        self.df_od_matrix           = df_od_matrix   # column names: idx, time, distance
        self.od_matrix              = {}      # (time, distance) = dictionary od_matrix['1-2']  # data from node 1-2 or 2-1
        self.weight_per_pallet_kg   = weight_per_pallet_lbs * 0.453592
        self.obj                    = obj                  # distance or time
        self.progress               = 0  # model run progress
        self.tsp_complete           = False
        
        self.vehicles               = []
        self.nodes                  = []
        self.initial_route          = []  # initial order of the nodes
        self.depot                  = None
        
        # call create_attributes class method
        self.create_attributes()

    def create_attributes(self):
        
        ## attribute self.od_matrix
        keys = self.df_od_matrix['idx']
        values = zip(self.df_od_matrix['time'], self.df_od_matrix['distance'])
        self.od_matrix = dict(zip(keys, values))
        # self.od_matrix['0-0'] = (0, 0)
        
        ## attribute self.nodes
        self.nodes = self.create_list_of_nodes()
        for node in self.nodes:
            if node.depot:
                self.depot = node
                break
        
        ## attribute self.initial_route
        self.vehicles = self.create_list_of_vehicles()

        ## attribute self.vehicles
        ## for initial route add the depot at the very end which means the truck will come back to the depot
        # 1. make sure the route starts from the depot
        for node in self.nodes:
            if node.depot:
                self.initial_route.insert(0, node)
            else:
                self.initial_route.append(node)
        # 2. the route ends at the depot
        self.initial_route.append(self.depot)
        

    def create_list_of_nodes(self):
        # merge the dataframes
        df = pd.merge(self.df_collection_points, self.df_unique_addresses, on="Account Name")
        
        node_list = []
        for index, row in df.iterrows():
            node = Node()
            
            node.id             = row['Index']
            node.account_id     = row['Account ID']
            node.account_name   = row['Account Name'].strip()  # remove leading and trailing whitespaces
            node.address        = row['Address']
            node.lat            = row['Lat']
            node.lon            = row['Lon']
            node.amount         = row['Amount (pallets)']
            if node.id == 0:
                node.depot      = True
                
            node_list.append(node)
        return node_list
    

    def create_list_of_vehicles(self):   
        truck_list = []
        i = 0
        for index, row in self.df_vehicles.iterrows():
            truck = Truck()
            
            truck.id                    = i
            truck.name                  = row['Name']
            truck.capacity              = row['Capacity (pallets)']
            truck.remaining_capacity    = row['Capacity (pallets)']
            truck.mass                  = row['Vehicle Weight (lbs)'] * 0.453592
            truck.engine_displacement   = row['Engine Size (Liter)']
            truck.frontal_area          = row['Frontal Area (square meter)']
            truck.engine_efficiency     = row['Engine Efficiency']
            truck.idle_engine_rpm       = row['Idle Engine RPM']
            truck.max_engine_rpm        = row['Max Engine RPM']
            
            truck_list.append(truck)  
            i += 1
        return truck_list


    
    @staticmethod
    # this function will return distance or time based on obj
    # distance or time from node i to j
    def calculate_distance(start_node, end_node, od_matrix, obj):
        i = start_node.id
        j = end_node.id
        if i > j:
            i , j = j, i
        key = f'{i}-{j}'
        time, distance = od_matrix[key]
        
        if obj == 'time':
            return time
        else:
            return distance

    @staticmethod
    def route_distance(route, od_matrix, obj):
        distance = 0
        for i in range(len(route)-1):
            start_node = route[i]
            end_node = route[i+1]
            distance += VRP.calculate_distance(start_node, end_node, od_matrix, obj)
        return distance

    @staticmethod    
    def calculate_fuel_rate (v, a, M, fi, k, N, V, C_d, C_r, rho, A, eta, e, U, g):   # ml/s
        alpha = fi*( k*N*V + (0.5*C_d*rho*A*v**3)/(1000*eta*e) )/U    
        beta = fi * ( a + g * C_r)*v/(1000*e*eta*U)    
        fuel_rate = alpha + beta*M         
        return fuel_rate 

    @staticmethod
    def speed_to_engine_rpm(speed_mph, min_rpm, max_rpm):
        max_rpm_ = 0.8*max_rpm
        min_speed = 0
        max_speed = 75
        
        rpm = min_rpm + (max_rpm_ - min_rpm)*speed_mph/(max_speed - min_speed)        
        return rpm   
    
    @staticmethod
    def calculate_fuel_consumption(route, vehicle, weight_per_pallet_kg, od_matrix):
        a   = 0
        fi  = vehicle.fuel_air_mass_ratio
        k   = vehicle.engine_friction_factor
        V   = vehicle.engine_displacement
        C_d = vehicle.c_d
        C_r = vehicle.mu_rr
        rho = vehicle.air_density
        A   = vehicle.frontal_area
        eta = vehicle.engine_efficiency
        e   = vehicle.drive_train_efficiency
        U   = vehicle.fuel_calorific_value
        g   = 9.81
        
        current_mass = vehicle.mass
        sum_fuel_gallon = 0
        for i in range(len(route)-1):
            start_node = route[i]
            end_node = route[i+1]
            current_mass += start_node.amount * weight_per_pallet_kg
            M = current_mass
            distance_mile = VRP.calculate_distance(start_node, end_node, od_matrix, obj = 'distance')
            time_hr = VRP.calculate_distance(start_node, end_node, od_matrix, obj = 'time')
            speed_mph = distance_mile/(time_hr + 1e-10)  # to avoid zero division error
            engine_rpm = max( vehicle.idle_engine_rpm, VRP.speed_to_engine_rpm(speed_mph, vehicle.idle_engine_rpm, vehicle.max_engine_rpm) )
            N = engine_rpm
            speed_mps = speed_mph * 0.44704
            v = speed_mps
            fuel_rate_ml_per_second = VRP.calculate_fuel_rate (v, a, M, fi, k, N, V, C_d, C_r, rho, A, eta, e, U, g)
            fuel_amount_ml = time_hr * 3600 * fuel_rate_ml_per_second
            fuel_amount_gallon = 0.000264172 * fuel_amount_ml
            sum_fuel_gallon += fuel_amount_gallon
            
        return sum_fuel_gallon        

    @staticmethod
    def gallon_to_CO2_lbs(gallon):  # fuel amount to CO2
        liter = gallon * 3.78541
        CO2_kg = liter * 2.65  # source:https://www.acea.be/news/article/differences-between-diesel-and-petrol#:~:text=The%20calorific%20value%20of%20diesel,to%2033.7%20MJ%2Flitre).
        CO2_lbs = 2.20462 * CO2_kg
        return CO2_lbs   
   
    @staticmethod
    def revise_route_order(route, vehicle, weight_per_pallet_kg, od_matrix):  # clockwise or anticlockwise order for minimum fuel consumption
        route_reverse_order = route.copy()
        route_reverse_order.reverse()
        fuel_reverse_route = VRP.calculate_fuel_consumption(route_reverse_order, vehicle, weight_per_pallet_kg, od_matrix) 
        fuel_original_route = VRP.calculate_fuel_consumption(route, vehicle, weight_per_pallet_kg, od_matrix)  
        if fuel_reverse_route < fuel_original_route:
            return route_reverse_order
        else:
            return route
        
    
        
    # update TSP progress attribute
    def update_tsp_progress(self, kk):
        i_max = 500
        percent_complete = min(100, (kk / i_max)*100 )
        # rescale, 100% -> 90%
        percent_complete = int( round(0.9 * percent_complete, 0) )
        self.progress = percent_complete
        
    
    def two_opt(self, route, od_matrix, obj, improvement_threshold=0.0001):
          best = route
          improved = True
          kk = 0
          # improvement_factor = 1
          while improved:
              improved = False
              for i in range(1, len(route)-2):
                    for j in range(i+1, len(route)):
                        if j-i == 1: continue # changes nothing, skip then
                        new_route = route[:]
                        new_route[i:j] = route[j-1:i-1:-1] # this is the 2woptSwap
    
                        best_distance = VRP.route_distance(best, od_matrix, obj)
                        new_distance = VRP.route_distance(new_route, od_matrix, obj)
                        if new_distance < best_distance:
                              best = new_route
                              # improved = True
                              improvement_factor = 1 - new_distance/best_distance # Calculate how much the route has improved
                              if improvement_factor > improvement_threshold:
                                  improved = True
                                  kk += 1
                                  # update TSP progress attribute
                                  if self.tsp_complete == False :
                                      self.update_tsp_progress(kk)
                                      
                                  
              route = best
              best_distance = VRP.route_distance(best, od_matrix, obj)
              
          return best, best_distance
    
    # create sub tour for the vehicles
    def create_sub_tour(self, route, vehicles): # list of vehicles 
        used_vehicles = []        
        
        ## 1. send vehicles to the nodes whose amount is atleast 70% of the vehicle capacity
        for i, vehicle in enumerate(vehicles):
            for j, node in enumerate(route):
                if node.depot == False and node.not_visited and (node.amount / vehicle.capacity) > 0.70 and (node.amount / vehicle.capacity) <= 1.0:
                    node.not_visited = False                    
                    vehicle.visited_nodes.append(node)
                    vehicle.remaining_capacity -= node.amount
                    used_vehicles.append(vehicle)
                    # update route and vehicle attributes
                    route[j] = node
                    vehicles[i] = vehicle # it will update the vehicle attributes like remaining capacity, visited nodes etc.
                    
                    # send this vehicle to the rest of the nodes and pick-up pallets if within capacity
                    remaining_route = route[j:]
                    for node in remaining_route:
                        if node.depot == False and node.not_visited and (node.amount <= vehicle.remaining_capacity):
                            node.not_visited = False
                            vehicle.visited_nodes.append(node)
                            vehicle.remaining_capacity -= node.amount
                            # update route and vehicle attributes
                            for k, o in enumerate(route):  # update route
                                if o.id == node.id:
                                    route[k] = node
                                    break
                            vehicles[i] = vehicle   # update vehicles
                            for k, o in enumerate(used_vehicles):  # update used_vehicles
                                if o.id == vehicle.id:
                                    used_vehicles[k] = vehicle  # it will update the vehicle attributes like remaining capacity, visited nodes etc.
                                    break
                            
        ## 2. send unused vehicles for the remaining unvisited nodes
        # remaining vehicles
        unused_vehicles = [vehicle for vehicle in vehicles if len(vehicle.visited_nodes) == 0]
        unused_vehicles.sort(key=lambda x: x.capacity, reverse=True)  # sort in descending order
        for i, vehicle in enumerate(unused_vehicles):
            for j, node in enumerate(route):
                if node.depot == False and node.not_visited and node.amount <= vehicle.remaining_capacity:
                    node.not_visited = False                    
                    vehicle.visited_nodes.append(node)
                    vehicle.remaining_capacity -= node.amount
                    used_vehicles.append(vehicle)
                    # update route and vehicles
                    route[j] = node
                    for k, o in enumerate(vehicles):  # update vehicles
                        if o.id == vehicle.id:
                            vehicles[k] = vehicle
                            break
                    
        ## 3. for the last vehicle, substitute with a vehicle whose capacity is close to the collected pallets  
        last_vehicle  = used_vehicles[-1]
        last_sub_tour = last_vehicle.visited_nodes
        ## consider as if the last vehicle was not used. we'll re-evaulate which vehicle is the right one to be assigned fot the last subtour
        used_vehicles.pop(-1)
        # update vehicles
        last_vehicle.visited_nodes = []
        last_vehicle.remaining_capacity = last_vehicle.capacity
        for k, o in enumerate(vehicles):  # update vehicles
            if o.id == last_vehicle.id:
                vehicles[k] = last_vehicle
                break
         
        unused_vehicles = [vehicle for vehicle in vehicles if len(vehicle.visited_nodes) == 0]
        unused_vehicles.sort(key=lambda x: x.capacity, reverse=False)  # sort in ascending order
        last_sub_tour_amount = sum([node.amount for node in last_sub_tour])
        for vehicle in unused_vehicles:
            if vehicle.capacity >= last_sub_tour_amount:
                vehicle.visited_nodes = last_sub_tour
                vehicle.remaining_capacity = vehicle.capacity - last_sub_tour_amount
                # update used_vehicles and vehicles
                used_vehicles.append(vehicle)
                for k, o in enumerate(vehicles):  # update vehicles
                        if o.id == vehicle.id:
                            vehicles[k] = vehicle
                            break
                break
        
        ## 4. for a final check, if any node is unvisited, send unused vehicle
        # remaining vehicles
        # unused_vehicles = list( set(vehicles) - set(used_vehicles) )
        unused_vehicles = [vehicle for vehicle in vehicles if len(vehicle.visited_nodes) == 0]
        unused_vehicles.sort(key=lambda x: x.capacity, reverse=True)  # sort in descending order
        for i, vehicle in enumerate(unused_vehicles):
            for j, node in enumerate(route):
                if node.depot == False and node.not_visited and node.amount <= vehicle.remaining_capacity:
                    node.not_visited = False                    
                    vehicle.visited_nodes.append(node)
                    vehicle.remaining_capacity -= node.amount
                    used_vehicles.append(vehicle)
                    # update route and vehicles
                    route[j] = node
                    for k, o in enumerate(vehicles):  # update vehicles
                        if o.id == vehicle.id:
                            vehicles[k] = vehicle
                            break        
        
        
        list_of_vehicles =  []
        
        vehicles.sort(key=lambda x: x.id, reverse=False)  # sort in ascending order
        for vehicle in vehicles:
            if vehicle.visited_nodes:
                sub_tour = vehicle.visited_nodes
                # add depot node at the begining and end of the subtour
                sub_tour.insert(0, self.depot)
                sub_tour.append(self.depot)
                vehicle.visited_nodes = sub_tour  # update attribute
                list_of_vehicles.append(vehicle)                
               
        return list_of_vehicles  # return list_of_vehicles with updated visited_nodes attribute
                


    def optimize_subtours(self, list_of_vehicles, weight_per_pallet_kg, od_matrix):
        
        updated_list_of_vehicles = []  # contains optimized visited nodes
        for vehicle in list_of_vehicles:
            ## optimize the subtours using Two Opt algorithm
            sub_tour = vehicle.visited_nodes            
            new_route, distance = self.two_opt(sub_tour, self.od_matrix, obj=self.obj, improvement_threshold=0.001)
            
            ## optimize the clockwise or anti-clockwise order of a subtour based on fuel consumption
            new_route = VRP.revise_route_order(new_route, vehicle, weight_per_pallet_kg, od_matrix)
            
            # update visited_nodes attribute
            vehicle.visited_nodes = new_route
            
            # update updated_list_of_vehicles
            updated_list_of_vehicles.append(vehicle)    
        
        return updated_list_of_vehicles
    


    # get angle between to points. This angle is required to rotate the arrow head for direction
    @staticmethod
    def get_angle(lat1, lon1, lat2, lon2):
        
        '''
        This function Returns angle value in degree from the location p1 to location p2   
        This function Return the vlaue of degree in the data type float
        
        Pleae also refers to for better understanding : https://gist.github.com/jeromer/2005586
        '''
        
        longitude_diff = np.radians(lon2 - lon1)
        
        latitude1 = np.radians(lat1)
        latitude2 = np.radians(lat2)
        
        x_vector = np.sin(longitude_diff) * np.cos(latitude2)
        y_vector = (np.cos(latitude1) * np.sin(latitude2) 
            - (np.sin(latitude1) * np.cos(latitude2) 
            * np.cos(longitude_diff)))
        angle = np.degrees(np.arctan2(x_vector, y_vector))
        
        # # # Checking and adjustring angle value on the scale of 360
        # if angle < 0:
        #     return angle + 360
        
        # Reducing 90 to account for the orientation of marker
        angle = angle - 90
        return angle



    # create interactive map in folium
    def create_html_map(self, list_of_vehicles):
        
        colors = ['orange', 'red', 'blue', 'green', 'purple', 'cadetblue', 'black', 'darkpurple', 'lightgreen', 'darkgreen', 'gray', 'darkred', 'lightblue', 'darkblue', 'lightred', 'pink', 'beige']
        
        feature_groups = []
        
        depot_location = (self.depot.lat, self.depot.lon)
        m = folium.Map(location = depot_location, zoom_start = 8)
        
        i = 0
        for vehicle in list_of_vehicles:
            sub_tour = vehicle.visited_nodes
            lons = [node.lon for node in sub_tour]  # list of lon
            lats = [node.lat for node in sub_tour]  # list of lat
            points = list(zip(lats, lons))
            feature_groups.append( folium.FeatureGroup(name= f'{list_of_vehicles[i].name} ({colors[i]})') )
            
            # polyline
            folium.PolyLine(points, color=colors[i], weight=5).add_to(feature_groups[i])
            
            # add direction to the route using Antpath
            AntPath(locations=points, reverse=False, color=colors[i], dash_array=[20, 30]).add_to(feature_groups[i])
        
            ## add arrow head for direction
            for k in range(len(lats)-1):
                lat1 = lats[k]
                lon1 = lons[k]
                
                lat2 = lats[k+1]
                lon2 = lons[k+1]
                
                lat_mid = (lat1 + lat2)/2
                lon_mid = (lon1 + lon2)/2
                
                folium.RegularPolygonMarker(location=(lat_mid, lon_mid), color=colors[i], fill_color=colors[i], number_of_sides=3, radius=10, rotation=VRP.get_angle(lat1, lon1, lat2, lon2)).add_to(feature_groups[i])
                
   
            
            # add points to popup addresses
            for node in sub_tour:
                html=f"""
                <div style="font-family: Arial; color: {colors[i]}">
                        <p> <b>Account #</b> {node.account_id}<br>
                            <b>Account Name :</b> {node.account_name}<br>
                            <b>Address      :</b> {node.address}
                        </p>
                </div>
                
                        """                
                iframe = folium.IFrame(html =  html,
                                       width = 500, 
                                       height = 80)
                
                popup = folium.Popup(iframe, min_width=300, max_width=600)  # min_width=300, max_width=600
                location = [node.lat, node.lon]
                
                folium.Marker(
                    location = location,
                    popup = popup,  # account name
                    icon = folium.Icon(color=colors[i], icon='map-marker'),  # 'map-marker', 'info-sign'
                ).add_to(feature_groups[i]) 
            
            m.add_child(feature_groups[i])
            
            i+=1
            
            # reset i value
            if i == len(colors):
                i = 0
            
        # turn on layer control
        m.add_child(folium.map.LayerControl())
        
        m.save("Route_map.html")




    def run(self):
        try:
            # run TSP
            route, distance = self.two_opt(self.initial_route, self.od_matrix, obj=self.obj, improvement_threshold=0.001)        
            self.tsp_complete = True # this portion is done to track progress            
                
            # create subtours
            list_of_vehicles = self.create_sub_tour(route, self.vehicles)
            self.progress = 92
            
            # optimize the individual subtours
            list_of_vehicles = self.optimize_subtours(list_of_vehicles, self.weight_per_pallet_kg, self.od_matrix) 
            travel_distance_list, travel_time_list, fuel_consumption_list, co2_emission_list, collected_amount_list, total_distance, total_time, total_collected_amount, total_fuel, total_co2, unvisited_accounts, uncollected_amount = self.subtour_stats(list_of_vehicles)
            self.progress = 98            
            
            # create interactive html map using folium
            self.create_html_map(list_of_vehicles)
            self.progress = 100
            
            # export some stats
            VRP.export_results(list_of_vehicles, travel_distance_list, travel_time_list, fuel_consumption_list, co2_emission_list, collected_amount_list, total_distance, total_time, total_collected_amount, total_fuel, total_co2)
            
    
            text = ''
            new_line = '\n'
            for idx, vehicle in enumerate(list_of_vehicles):
                subtour = vehicle.visited_nodes
                subtour_account_names = [node.account_name for node in subtour]  
                
                under_line = '=' * len(vehicle.name)    
                text = text + f'{new_line}{vehicle.name} {new_line}{under_line}{new_line}\
Route: {subtour_account_names} {new_line}\
Travel distance      : {travel_distance_list[idx]: ,.1f} miles {new_line}\
Travel time          : {travel_time_list[idx]: ,.1f} hours {new_line}\
Fuel burnt           : {fuel_consumption_list[idx]: ,.1f} gallons {new_line}\
CO2 emission         : {co2_emission_list[idx]: ,.1f} lbs {new_line}\
Miles per gallon     : {travel_distance_list[idx] / (fuel_consumption_list[idx] + 1e-10): ,.1f} {new_line}\
Collected amount     : {collected_amount_list[idx]: ,.0f} pallets {new_line}\
Capacity utilization : {collected_amount_list[idx] / list_of_vehicles[idx].capacity *100: ,.0f}% {new_line}'
    
            if len(unvisited_accounts) == 0:
                unvisited_account_names = 'None'
            else:
                unvisited_account_names = unvisited_accounts
            overall_summary = f'{new_line}Overall Summary{new_line}==============={new_line}\
Total distance          : {total_distance: ,.0f} miles {new_line}\
Total collected amount  : {total_collected_amount: ,.0f} pallets {new_line}\
Unvisited account names :  {unvisited_account_names} {new_line}\
Uncollected amount      : {uncollected_amount: ,.0f} pallets'          
            
            text += overall_summary
            self.text = text
        
        except Exception as e: 
            self.text = f'{type(e).__name__}: {e.args}'

        
        
    def subtour_stats(self, list_of_vehicles):
        # find the travel_distance, travel_time, fuel_consumption, co2_emission and colleccted load
        travel_distance_list    = [] # mile
        travel_time_list        = [] # hours
        fuel_consumption_list   = [] # gallons
        co2_emission_list       = [] # lbs
        collected_amount_list   = [] # pallets
        
        total_distance = 0
        total_time = 0
        total_collected_amount = 0
        total_fuel = 0
        total_co2 = 0
        
        visited_accounts = set()
        all_accounts = set()
        total_amount = 0
        
        for vehicle in list_of_vehicles:
            subtour = vehicle.visited_nodes
            time_sum = 0
            distance_sum = 0
            for k in range(len(subtour) - 1):
                start_node  = subtour[k]
                end_node    = subtour[k + 1]
                i = start_node.id
                j = end_node.id            
                if i > j:
                    i , j = j, i
                key = f'{i}-{j}'            
                time, distance = self.od_matrix[key]
                time_sum += time
                distance_sum += distance
                total_distance += distance
                total_time += time
                
            travel_time_list.append(time_sum)
            travel_distance_list.append(distance_sum)
            
            amount_sum = 0            
            for node in subtour:
                amount_sum += node.amount
                total_collected_amount += node.amount
                visited_accounts.add(node.account_name)
            
            collected_amount_list.append(amount_sum)
            
            fuel_gallons = VRP.calculate_fuel_consumption(subtour, vehicle, self.weight_per_pallet_kg, self.od_matrix)
            fuel_consumption_list.append(fuel_gallons)
            total_fuel += fuel_gallons
            
            co2_lbs = VRP.gallon_to_CO2_lbs(fuel_gallons)
            co2_emission_list.append(co2_lbs)
            total_co2 += co2_lbs
            
        # all account names
        for node in self.nodes:
            all_accounts.add(node.account_name)
            total_amount += node.amount
            
        unvisited_accounts = list(all_accounts - visited_accounts)
        uncollected_amount = total_amount - total_collected_amount
            
            
            
        return travel_distance_list, travel_time_list, fuel_consumption_list, co2_emission_list, collected_amount_list, total_distance, total_time, total_collected_amount, total_fuel, total_co2, unvisited_accounts, uncollected_amount

                
    @staticmethod
    def export_results(list_of_vehicles, travel_distance_list, travel_time_list, fuel_consumption_list, co2_emission_list, collected_amount_list, total_distance, total_time, total_collected_amount, total_fuel, total_co2):
        mpg_list = []
        for fuel, distance in zip(fuel_consumption_list, travel_distance_list):
            mpg = distance / fuel
            mpg_list.append(mpg)
        
        vehicle_names = [vehicle.name for vehicle in list_of_vehicles]
        data = [vehicle_names,
                collected_amount_list,
                travel_distance_list, 
                travel_time_list, 
                fuel_consumption_list, 
                mpg_list,
                co2_emission_list]
        
        overall_mpg = total_distance / total_fuel
        
        # create data frame and transpose
        df = pd.DataFrame(data).transpose()
        
        # add overall stats
        df.loc[len(df.index)] = ['Overall Statistics', total_collected_amount, total_distance, total_time, total_fuel, overall_mpg, total_co2]
      
        # column names
        df.columns = ['Vehicles', 'Collected Amount (pallets)', 'Travel Distance (miles)', 'Travel Time (hours)', 'Fuel (gallons)', 'MPG', 'CO2 Amount (lbs)' ]
 
        # export to a csv file
        file_name = 'Transportation_model_output.csv'
        with open(file_name, 'w') as f:           # Drop to csv w/ context manager
            df.to_csv(f, sep=',', index=False, encoding='utf-8', line_terminator='\n')         
        
if __name__ == '__main__':
    
    # # read necessary data
    df_vehicles = pd.read_excel(io = 'TEMPLATE_transportation_model.xlsm', sheet_name = 'Vehicle List')
    df_collection_points = pd.read_excel(io = 'TEMPLATE_transportation_model.xlsm', sheet_name = 'Collection Addresses')
    df_unique_addresses = pd.read_csv('ActiveAccounts_Unique.csv')  
    df_od_matrix = pd.read_csv('ActiveAccounts_OD.csv')
    
        
    # create VRP model    
    model = VRP(df_vehicles, df_od_matrix, df_collection_points, df_unique_addresses, obj = 'time', weight_per_pallet_lbs = 500)
    model.run()
    
    print(model.text)
    
    

