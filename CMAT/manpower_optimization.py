from HACO_parallel import HACO
from process_model import prepare_process_model_data, SimTimeData, Warehouse_simulation
import warnings
warnings.filterwarnings("ignore")


class Optimization:
    def __init__(self, energy_cost_per_kwh, available_operators, weeks, days, shifts, hours, excel_file_name, population, max_iteration, max_run_time, probability_random_chicks = 0.1, max_step = 0.99, min_step = 0.01):
        self.available_operators        = available_operators
        self.sim_time_data              = SimTimeData()
        self.sim_time_data.sim_time     = weeks * days * shifts * hours * 60    # simulation time in minutes
        self.sim_time_data.energy_cost_per_kwh = energy_cost_per_kwh
        self.process_model_data         = prepare_process_model_data(excel_file_name)
        self.manual_work_station_names  = []
        self.dismantling_station_names  = []

        self.population                 = population
        self.max_iteration              = max_iteration
        self.max_run_time               = max_run_time
        self.probability_random_chicks  = probability_random_chicks
        self.max_step                   = max_step
        self.min_step                   = min_step
        self.y_best                     = 0.0   # placeholder for best objective value
        self.x_best                     = []    # placeholder for best solution
        self.text                       = ''
        self.optimization_complete      = False

        for data in self.process_model_data:
            if data['TYPE'] == 'Manual Work Station':
                self.manual_work_station_names.append(data['NAME'])
            elif data['TYPE'] == 'Dismantling Station':
                self.dismantling_station_names.append(data['NAME'])
            else:
                pass


        self.lb = [1] * ( len(self.manual_work_station_names) + len(self.dismantling_station_names) )
        self.ub = [self.available_operators] * ( len(self.manual_work_station_names) + len(self.dismantling_station_names) )

    def objective_function(self, xx):  # xx = [res_sorting, bus_sorting, crt_dism, lcd_dism, std_dism]

        # Change process_model_data attributes
        i = 0
        for name in self.manual_work_station_names:
            for data in self.process_model_data:
                if data['NAME'] == name:
                    data['NO OF OPERATORS'] = xx[i]
                    i += 1
        for name in self.dismantling_station_names:
            for data in self.process_model_data:
                if data['NAME'] == name:
                    data['NO OF OPERATORS'] = xx[i]
                    i += 1


        ws = Warehouse_simulation(self.process_model_data, self.sim_time_data)
        ws.run_simulation()
        per_lb_cost = sum(x * y for x, y in zip(ws.overall_input_mass_dist, ws.item_wise_processing_cost_per_lb))/sum(ws.overall_input_mass_dist)

        return per_lb_cost

    def run_HACO(self):
        y_best, x_best = HACO(self.objective_function, self.lb, self.ub, self.available_operators, self.population, self.max_iteration, self.max_run_time, self.probability_random_chicks, self.max_step, self.min_step)
        self.y_best = y_best
        self.x_best = x_best
        new_line = '\n'
        self.text += f"Processing cost after optimization (USD/lb): {round(y_best, 4)} {new_line}{new_line}\
Recommended Manpower {new_line}\
-------------------- {new_line}"
        i = 0
        for name in self.manual_work_station_names:
            self.text += f"{name} : {x_best[i]} {new_line}"
            i += 1
        for name in self.dismantling_station_names:
            self.text += f"{name} : {x_best[i]} {new_line}"
            i += 1

        self.optimization_complete = True

if __name__ == "__main__":
    # Set parameter values for HACO algorithm
    population = 4
    # probability_random_chicks = 0.1
    # max_step = 0.99
    # min_step = 0.01
    max_iteration = 1
    max_run_time = 3600 # max_run_time in minutes

    energy_cost_per_kwh = 0.11
    available_operators = 20
    weeks = 1/5
    days = 5
    shifts = 1
    hours = 8
    excel_file_name = 'TEMPLATE_process_model_data_sample.xlsx'


    optimization = Optimization(energy_cost_per_kwh, available_operators, weeks, days, shifts, hours, excel_file_name, population, max_iteration, max_run_time)
    optimization.run_HACO()
    print(optimization.text)
