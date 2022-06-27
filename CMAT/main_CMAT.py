"""
@author: Mamunur Rahman
"""



import ctypes

import pandas as pd
# from PyQt5 import QtGui as qtg
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor, QIcon, QFont
# from PyQt5 import uic

from PyQt5 import QtTest
import sys
# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog
from PyQt5.uic import loadUi

# from vrp import VRP   # transportation module
from vrp_model import VRP
from address_adder import AddressAdder
from process_model import prepare_process_model_data, SimTimeData, Warehouse_simulation   # process model
from economic_model import EconomicData, EconomicModel   # economic model
from generate_text import generateText

from show_plot import ShowProcessPlot, ShowEconomicPlot, ShowTransportationPlot
# from customized_HACO_parallel import HACO
# from optimization_objective_function import objective_function





class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        """MainWindow constructor."""
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi("main_window.ui", self)
        
        # set icon
        # self.setWindowIcon(QIcon('app_icon.png'))
        app_icon = QIcon()
        app_icon.addFile('app_icon1.png', QtCore.QSize(16, 16))
        app.setWindowIcon(app_icon)

        # # Code starts from here        
        # self.ui = Ui_main_window()        
        # self.ui.setupUi(self)
        # # Add menu bar
        # self.menu_bar()
        
        self.thread={}
        
        # # Fix the window size
        # self.setFixedSize(950, 420)
        # Add tool bar
        self.tool_bar()

        
        
        self.text = generateText()
        
        # create instances of different windows
        self.process_model_window = process_model_window()
        self.choose_economic_model_options = ChooseEconomicModel()
        self.economic_model_window = Economic_model_window_1()
        self.process_model_result_window = ProcessModelResultWindow()
        self.economic_model_result_window = EconomicModelResultWindow()        
        self.transportation_model_window = Transportation_input_window()
        self.transportation_model_result_window = TransportationModelResultWindow()
        
        ## connect main window buttons
        # connect process_model_btn
        self.process_model_btn.clicked.connect(self.process_model)
        # connect economic_model_btn
        self.economic_model_btn.clicked.connect(self.choose_economic_model)
        # connect transportation_model_btn
        self.transportation_model_btn.clicked.connect(self.choose_transportation_model)
        
        
        # output window for tool bar output like about, user agreement etc.
        self.output_window = OutputWindow()
        
        
        self.output_window.close_button.clicked.connect(self.outputWindowCloseButton)
        # connect main window exit button
        self.exit_btn.clicked.connect(self.close)        
        
        
        # # connect run_button
        # self.run_button.clicked.connect(self.runOutput)

        # #connect browse button
        # self.browse_button.clicked.connect(self.browseFile)
        # # connect clear button
        # self.clear_button.clicked.connect(self.clear_inputs)     

        
        # # create result window for displaying results
        # self.result_window = ResultWindow()
        
        # call method to change the cursor style when hovered on a button
        self.button_hover()
        
        
    # change button style when hovered on a button
    # setting background color to push button when mouse hover over it
    def button_hover(self):
        button_list = [
            self.transportation_model_btn,  # main window buttons
            self.process_model_btn,
            self.economic_model_btn,
            self.exit_btn,
            self.output_window.close_button, # tool bar output window buttons
            self.process_model_window.browse_btn, # process model window buttons
            self.process_model_window.exit_btn,
            self.process_model_window.run_btn,
            self.process_model_result_window.close_btn, # process model result window buttons
            self.process_model_result_window.plot_utilization_storage_areas_button,
            self.process_model_result_window.plot_utilization_manual_work_stations_button,
            self.process_model_result_window.plot_output_button,
            self.process_model_result_window.plot_category_wise_processing_cost_button,
            self.process_model_result_window.plot_utilization_shredding_stations_button,
            self.economic_model_window.exit_btn, # economic model window buttons
            self.transportation_model_window.run_btn, # transportation model window buttons
            self.transportation_model_window.exit_btn,
            self.transportation_model_result_window.close_btn, # transportation model result window buttons
            self.transportation_model_result_window.interactive_plot_button,
            ]
        
        for button in button_list:
            button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            # button.setStyleSheet("QPushButton::hover"
            #                       "{"
            #                       "background-color : lightgreen;"
            #                       "}")            
        
        
    
        
    # # Menu bar
    # def menu_bar(self):    

    #     menu = self.menuBar() # -> QMenuBar
    #     file_menu = menu.addMenu('Menu') # -> QMenu
    #     #User agreement
    #     file_menu.addAction('User Agreement', self.userAgreement) # -> QAction
    #     #  About this software
    #     file_menu.addAction('About', self.aboutInfo)
    #     #  Clear output window
    #     file_menu.addAction('Clear', self.clear_window)
    #     #  Exit application
    #     file_menu.addAction('Exit Application', self.close)
    

    
    # Tool Bar
    def tool_bar(self):        
        # toolbar = self.addToolBar('Miscellaneous')
        toolbar = self.toolBar
        # To use an icon, add it in as the first argument
        toolbar.addAction('About', self.aboutInfo)
        toolbar.addAction('License', self.userAgreement)
        toolbar.addAction('User Manual', self.userManual)
        toolbar.addAction('Contact Info', self.contactInfo)
        # toolbar.addAction('Exit', self.close)
        toolbar.setFont(QFont('Times', 20))  # it is not working


    # toolbar output window close button
    def outputWindowCloseButton(self):
        self.show()  # show the main window
        self.output_window.close()  # close the output window
                
    def processModelExitButton(self):
        self.show()  # show the main window
        self.process_model_window.close()  # close the process model input window
                # close the threads
        try:
            self.thread[1].terminate()
            self.thread[2].terminate()
        except:
            pass
        # self.process_model_window = None
                
    def modelExitButtonAction(self, source):
        self.show()  # show the main window
        if source == 'economic_model':
            self.economic_model_window.close()  # close the rconomic model input window
        elif source == 'process_model':
            self.process_model_window.close()  # close the process model input window
        elif source == 'transportation_model':
            self.transportation_model_window.close()  # close the transportation model input window
        
        else:
            pass
             
        
    def userAgreement(self):
        # self.hide()  # hide the main window
        self.output_window.output.setText(self.text.user_agreement)
        self.output_window.show()
        self.output_window.setWindowTitle('User Agreement')
        
        
        
    def aboutInfo(self):
        # self.hide()  # hide the main window
        self.output_window.output.setText(self.text.about_info)
        self.output_window.show()
        self.output_window.setWindowTitle('About')
        
        
    def userManual(self):
        # self.hide()  # hide the main window
        self.output_window.output.setText(self.text.user_manual)
        self.output_window.show()
        self.output_window.setWindowTitle('User Manual')
        
    def contactInfo(self):
        # self.hide()  # hide the main window
        self.output_window.output.setText(self.text.contact_info)
        self.output_window.show()
        self.output_window.setWindowTitle('Contact Information')
    
           
    # for process and economic model            
    def browseFile(self, source):
        fileNameTuple = QFileDialog.getOpenFileName(self, 'OpenFile',"", "(*.xls *.xlsx *.csv)")
        fileName = fileNameTuple[0]
        self.file_name = fileName
        # show the file name in QLineEdit box
        file_name_with_path = self.file_name.split("/")
        excel_file_name = f'{file_name_with_path[0]}\ .. \{file_name_with_path[-1]}'        

        if source == 'economic_model' :
            self.economic_model_window.selected_file_box.setText(excel_file_name)
        elif source == 'process_model' :
            self.process_model_window.selected_file_box.setText(excel_file_name)


    def choose_transportation_model(self):
        # create choose transportation model options window
        self.choose_transportation_model_options = ChooseTransportationModel()
        self.choose_transportation_model_options.show()
        
        ## connect buttons
        self.choose_transportation_model_options.next_btn.clicked.connect(self.transportation_model)
        self.choose_transportation_model_options.cancel_btn.clicked.connect(self.choose_transportation_model_options.close)    



    # for transportation model  
    def browseFileTransporttaionModel(self, source):
        fileNameTuple = QFileDialog.getOpenFileName(self, 'OpenFile',"", "(*.xls *.xlsx *.csv *.xlsm)")
        fileName = fileNameTuple[0]
        
        file_location = fileName.split("/")
        file_location.pop()
        self.html_file_path = ''  # html_file_path will be used to read the produced 'Route_map.html' file 
        for text in file_location:
            self.html_file_path += f'{text}/'
        
        if source == 'transportation_model_collection_point_data':
            self.file_name_collection_point_data = fileName            
            # show the file name in QLineEdit box
            self.transportation_model_window.selected_file_box_1.setText(self.file_name_collection_point_data)
        
        elif source == 'transportation_model_unique_address_data':
            self.file_name_unique_address_data = fileName            
            # show the file name in QLineEdit box
            self.transportation_model_window.selected_file_box_2.setText(self.file_name_unique_address_data)
        
        elif source == 'transportation_model_od_matrix_data':
            self.file_name_od_matrix_data = fileName            
            # # show the file name in QLineEdit box
            # file_name_with_path = self.file_name_od_matrix_data.split("/")
            # csv_file_name = f'{file_name_with_path[0]}\ .. \{file_name_with_path[-1]}'
            self.transportation_model_window.selected_file_box_3.setText(self.file_name_od_matrix_data)


    def addressAdderExitButtonAction(self):
        self.show()  # show the main window
        self.address_adder_window.close()  # close the address adder window        

        
    def transportation_model(self):
        # option 1 selected (address adder)
        if self.choose_transportation_model_options.radioButton_1.isChecked():
            self.address_adder_window = AddressAdder()
            self.address_adder_window.show()
            self.hide()  # hide the main window
            self.choose_transportation_model_options.close()  # close the choose_transportation_model_options window
            
            # connect the address adder window 'exit' button
            self.address_adder_window.ui.btnExit.clicked.connect(self.addressAdderExitButtonAction)

        # option 2 selected (transportation model)
        elif self.choose_transportation_model_options.radioButton_2.isChecked():
            # create transportation model window
            self.transportation_model_window = Transportation_input_window()
            # call button_hover method
            self.button_hover()
    
            self.transportation_model_window.show()  #show the transportation model window
            self.hide()  # hide the main window
            self.choose_transportation_model_options.close()  # close the choose_transportation_model_options window
            
            ## connect buttons        
            # browse_btn_collection_point_data
            self.transportation_model_window.browse_btn_collection_point_data.clicked.connect(lambda: self.browseFileTransporttaionModel(source = 'transportation_model_collection_point_data'))
            # browse_btn_unique_address_data
            self.transportation_model_window.browse_btn_unique_address_data.clicked.connect(lambda: self.browseFileTransporttaionModel(source = 'transportation_model_unique_address_data'))
            # browse_btn_od_matrix_data
            self.transportation_model_window.browse_btn_od_matrix_data.clicked.connect(lambda: self.browseFileTransporttaionModel(source = 'transportation_model_od_matrix_data'))
            
            #connect run button
            self.transportation_model_window.run_btn.clicked.connect(self.transportation_model_output)  
            # exit button
            self.transportation_model_window.exit_btn.clicked.connect(lambda: self.modelExitButtonAction(source = 'transportation_model'))
       


    def process_model(self):
        # create process model window
        self.process_model_window = process_model_window()
        # call button_hover method
        self.button_hover()

        # self.process_model_result_window.close()
        self.process_model_window.show()  #show the process model window
        self.hide()  # hide the main window
        
        # connect buttons
        self.process_model_window.exit_btn.clicked.connect(lambda: self.modelExitButtonAction(source = 'process_model'))
        #connect browse button
        self.process_model_window.browse_btn.clicked.connect(lambda: self.browseFile(source = 'process_model'))
        #connect run button
        self.process_model_window.run_btn.clicked.connect(self.process_model_output)
 
    
    # def optimization_model_input(self):
    #     self.optimization_input_window = Optimization_input_window()
        
    #     # show optimization input window
    #     self.optimization_input_window.show()
    #     # hide process model window
    #     self.process_model_window.hide()
        
    #     # change mouse icon when hover over buttons
    #     button_list = [self.optimization_input_window.exit_btn,
    #                     self.optimization_input_window.run_btn,
    #                     ]
    #     for button in button_list:
    #         button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        
        
    #     # connect buttons
    #     self.optimization_input_window.run_btn.clicked.connect(self.run_optimization)
    #     self.optimization_input_window.exit_btn.clicked.connect(self.optimizationInputExitButton)
        
    # def optimizationInputExitButton(self):
    #     self.process_model_window.show()
    #     self.optimization_input_window.close()
        
        
        
    # def run_optimization(self):
    #     # data
    #     lb = [1]  * 5 # 5 -> five work stations
    #     ub = [10] * 5
        
    #     # call read_process_model_data method to read user input data
    #     self.read_process_model_data()
    #     data = self.process_model_data
    #     available_operators =   data.res_sorting_operator      + \
    #                             data.bus_sorting_operator      + \
    #                             data.dismantling_operator_crt  + \
    #                             data.dismantling_operator_lcd  + \
    #                             data.dismantling_operator_std
                
    #     lb = [1]  * 5 # 5 -> five work stations
    #     ub = [available_operators] * 5
    #     # Set parameter values for HACO algorithm
    #     population      = int( self.optimization_input_window.population.text() )
    #     max_step        = self.optimization_input_window.max_step_size.value()
    #     min_step        = self.optimization_input_window.min_step_size.value()
    #     max_iteration   = self.optimization_input_window.max_iteration.value()
    #     max_run_time    = self.optimization_input_window.max_run_time.value() * 3600  # hour --> seconds
    #     probability_random_chicks = 0.0
        
        
    #     # call optimization algorithm
    #     HACO(objective_function, data, lb, ub, available_operators, population, probability_random_chicks, max_step, min_step, max_iteration, max_run_time)
 

        
        
    
    def choose_economic_model(self):
        # create choose economic model options window
        self.choose_economic_model_options = ChooseEconomicModel()
        self.choose_economic_model_options.show()
        
        # connect buttons
        self.choose_economic_model_options.next_btn.clicked.connect(self.economic_model)
        self.choose_economic_model_options.cancel_btn.clicked.connect(self.choose_economic_model_options.close)
    
  
      
    
    def economic_model(self):
        
        # option 1 selected (independent run)
        if self.choose_economic_model_options.radioButton_1.isChecked():
            # create attribute and set value as True
            self.economic_model_option_1 = True
            self.economic_model_option_2 = False
            # close choose_economic_model_options window
            self.choose_economic_model_options.close()
        
            # create economic model window
            self.economic_model_window = Economic_model_window_1()
            # call button_hover method
            self.button_hover()
    
            self.economic_model_window.show()  #show the economic model window
            self.hide()  # hide the main window
            
            # connect buttons
            self.economic_model_window.exit_btn.clicked.connect(lambda: self.modelExitButtonAction(source = 'economic_model'))
            #connect browse button
            self.economic_model_window.browse_btn.clicked.connect(lambda: self.browseFile(source = 'economic_model'))
            #connect run button
            self.economic_model_window.run_btn.clicked.connect(self.economic_model_output)
            
        # option 2 selected (get data from process model)
        if self.choose_economic_model_options.radioButton_2.isChecked():
            # create attribute and set value as True
            self.economic_model_option_2 = True
            self.economic_model_option_1 = False
            # close choose_economic_model_options window
            self.choose_economic_model_options.close()
        
            # create economic model window
            self.economic_model_window = Economic_model_window_2()
            # change mouse icon when hover over buttons
            button_list = [self.economic_model_window.exit_btn,
                           self.economic_model_window.run_btn,
                           ]
            for button in button_list:
                button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    
            self.economic_model_window.show()  #show the economic model window
            self.hide()  # hide the main window
            
            # connect buttons
            self.economic_model_window.exit_btn.clicked.connect(lambda: self.modelExitButtonAction(source = 'economic_model'))
            #connect browse button
            self.economic_model_window.browse_btn.clicked.connect(lambda: self.browseFile(source = 'economic_model'))
            #connect run button
            self.economic_model_window.run_btn.clicked.connect(self.economic_model_output)
        
        

    def read_process_model_data(self):
        
        # create an instance of ProcessData
        self.sim_time_data = SimTimeData()
        
        ## change the process_data attributes as per user input
        # simulation time in minutes
        self.sim_time_data.weeks                      = self.process_model_window.spin_box_weeks.value()
        self.sim_time_data.days                       = self.process_model_window.spin_box_days.value()
        self.sim_time_data.shifts                     = self.process_model_window.spin_box_shifts.value()
        self.sim_time_data.hours                      = self.process_model_window.spin_box_hours.value()
        self.sim_time_data.sim_time                   = self.sim_time_data.weeks * self.sim_time_data.days * self.sim_time_data.shifts * self.sim_time_data.hours * 60
        self.sim_time_data.energy_cost_per_kwh        = float( self.process_model_window.energy_cost_per_kwh.text() )        
        
        
        # read data from excel file      
        self.process_model_data = prepare_process_model_data(self.file_name)
        
        # # want to optimize operator allocation?
        # text = str(self.process_model_window.optimization_comboBox.currentText())
        # self.do_optimization = text

        
    def process_model_output(self):
        # read data
        self.read_process_model_data()
        
        # if self.do_optimization =='No':        
        
        self.process_model_result_window.show()  #show the output window
        self.process_model_window.hide()  #hide the process model window
        # self.process_model_result_window.setWindowTitle('Click the Show Simulation Results button when run is complete')  # set this title while the application is running
        
        self.bar = ProgressBarWindow()
        self.thread[1] = ThreadClass_WS(self.bar, self.process_model_data, self.sim_time_data)
        self.thread[1].start()
        
        self.bar.show()
        self.bar.show_result_btn.setEnabled(False)
        self.bar.show_result_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.thread[2] = ThreadClass_progress_bar_ws(self.thread[1].ws)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.updateProgressBar)
        
        self.thread[2].finished.connect(self.show_simulation_results)  # show the results when finished
        
        
        # connect buttons
        self.process_model_result_window.close_btn.clicked.connect(self.processModelResultCloseButton)
        self.bar.show_result_btn.clicked.connect(self.show_simulation_results)
        
        # create plot_window which is a instance of ShowPlot class
        self.plot_window = ShowProcessPlot(self.thread[1].ws)
        
        # connect plot buttons
        self.process_model_result_window.plot_utilization_storage_areas_button.clicked.connect(lambda: self.generatePlotProcessModel(source = 'utilization_storage_areas'))
        self.process_model_result_window.plot_utilization_manual_work_stations_button.clicked.connect(lambda: self.generatePlotProcessModel(source = 'utilization_manual_ws'))
        self.process_model_result_window.plot_output_button.clicked.connect(lambda: self.generatePlotProcessModel(source = 'output'))
        self.process_model_result_window.plot_category_wise_processing_cost_button.clicked.connect(lambda: self.generatePlotProcessModel(source = 'processing_cost'))
        self.process_model_result_window.plot_utilization_shredding_stations_button.clicked.connect(lambda: self.generatePlotProcessModel(source = 'utilization_shredding_stations'))
            
        # if self.do_optimization =='Yes':
        #     self.optimization_model_input()
    
    def processModelResultCloseButton(self):
        self.process_model_window.show()  #show the process model window
        self.process_model_result_window.close()
        
        # close the threads
        try:
            self.thread[1].terminate()
            self.thread[2].terminate()
        except:
            pass

        
    # generate plot for process model when different buttons are pressed
    def generatePlotProcessModel (self, source):
        self.plot_window.show()  #show the plot window
        if source == 'output':
            self.plot_window.plot_output()
        elif source == 'processing_cost':
            self.plot_window.plot_ctegory_wise_processing_cost()
        elif source == 'utilization_storage_areas':
            self.plot_window.plot_utilization_storage_area()  
        elif source == 'utilization_manual_ws':
            self.plot_window.plot_utilization_manual_work_station() 
        elif source == 'utilization_shredding_stations':
            self.plot_window.plot_utilization_shredding_stations()
            
        
    
    def show_simulation_results(self):
        self.process_model_result_window.output.setText(self.thread[1].text) 
        # set window title
        self.process_model_result_window.setWindowTitle('Output')
        self.bar.close()
        
        # self.thread[1].terminate()
        # self.thread[2].terminate()
        
    
    def updateProgressBar(self, value):
            self.bar.progressBar.setValue(value)





    def transportation_model_output(self):
        # read data for transportation model
        df_collection_points = pd.read_excel(io = self.file_name_collection_point_data, sheet_name = 'Collection Addresses')
        df_vehicles = pd.read_excel(io = self.file_name_collection_point_data, sheet_name = 'Vehicle List')
        df_unique_addresses = pd.read_csv(self.file_name_unique_address_data)
        df_od_matrix = pd.read_csv(self.file_name_od_matrix_data)
        
        # get data from user input
        weight_per_pallet_lbs = float( self.transportation_model_window.weight_per_pallet_lbs.text() )
        
        objective = str(self.transportation_model_window.objective_comboBox.currentText())
        if objective == 'Travel Time':
            obj = 'time'
        else:
            obj = 'distance'
            
        self.bar = ProgressBarWindow()
        self.thread[1] = ThreadClass_TM(self.bar, df_od_matrix, df_collection_points, df_vehicles, df_unique_addresses, obj, weight_per_pallet_lbs)
        self.thread[1].start()
        
        self.bar.show()
        self.bar.show_result_btn.setEnabled(False)
        self.bar.show_result_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.thread[2] = ThreadClass_progress_bar_TM(self.thread[1].transport_model)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.updateProgressBar)  
      
        # connect buttons
        self.bar.show_result_btn.clicked.connect(self.show_transportation_model_results)


    def show_transportation_model_results(self):
        self.transportation_model_result_window.show()  # show transportation_model_result_window
        self.transportation_model_window.hide()  #hide the transportationc model input window
        
        self.transportation_model_result_window.output.setText(self.thread[1].text) 
        self.bar.close()
        
        # connect buttons
        self.transportation_model_result_window.close_btn.clicked.connect(self.transportationModelResultCloseButton)
        # show interactive plot button
        self.transportation_model_result_window.interactive_plot_button.clicked.connect(self.transportationModelInteractiveMap)

    def transportationModelResultCloseButton(self):
        self.transportation_model_window.show()  # show the transportationc model input window
        self.transportation_model_result_window.close() # close transportation_model_result_window
        # terminate the threads
        self.thread[1].terminate()
        self.thread[2].terminate()
        
        
    def transportationModelInteractiveMap(self):
        self.transportation_map = ShowTransportationPlot(self.html_file_path)
        self.transportation_map.show()
        
        
        
        
        

    def economic_model_output(self):           
            self.economic_model_result_window.show()  #show the output window
            self.economic_model_window.hide()  #hide the economic model window
            
            try:
                # create data
                data = EconomicData(excel_file_name = self.file_name)
                
                ## read user input Cost data
                # for independent run
                if self.economic_model_option_1:
                    data.cost_dict['Total sorting labor cost per month'] = [int( self.economic_model_window.sorting_labor.text() ) ]
                    data.cost_dict['Total dismantling labor cost per month'] = [int( self.economic_model_window.dismantling_labor.text() )]
                    data.cost_dict['Total shredding labor cost per month'] = [int( self.economic_model_window.shredding_labor.text() )]
                    
                    data.cost_dict['CRT tube treatment cost per lb'] = [float( self.economic_model_window.crt_tube_treatment_cost.text() )]
                    data.cost_dict['Battery treatment cost per lb'] = [float( self.economic_model_window.battery_treatment_cost.text() )]
                    
                # some data from process model
                if self.economic_model_option_2:
                    data.cost_dict['fraction_of_utility_cost_from_shop_floor_machines'] = float( self.economic_model_window.fraction_of_utility_cost_from_shop_floor_machines.text() )
                    # data.cost_dict['fraction_of_utility_cost_from_shop_floor_machines'] = 0.7
                
                # common data
                data.cost_dict['Total fixed manufacturing overhead per month'] = int( self.economic_model_window.fixed_manufacturing_overhead.text() )
                data.cost_dict['Repair and maintenance cost per month'] = int( self.economic_model_window.repair_and_maintenance.text() )
                data.cost_dict['Warehouse misc operating cost per month'] = int( self.economic_model_window.warehouse_misc_operating_cost.text() )
                data.cost_dict['Transportation cost per month'] = int( self.economic_model_window.transportation.text() )
                data.cost_dict['Utility cost per month'] = [int( self.economic_model_window.utility_cost.text() )]
                data.cost_dict['Fraction of overhead cost coming from top e-waste items'] = float( self.economic_model_window.fraction_of_overhead_cost_from_top_ewastes.text() )
                
                
                # read user input Freight and Fees per lb by Smelters data
                data.price_dict['hdd_shred_fees_and_freight_per_lb'] = float( self.economic_model_window.hdd_shred.text() )
                data.price_dict['cee_shred_fees_and_freight_per_lb'] = float( self.economic_model_window.cee_shred.text() )
                data.price_dict['motherboard_shred_fees_and_freight_per_lb'] = float( self.economic_model_window.motherboard_shred.text() )
                data.price_dict['tv_shred_fees_and_freight_per_lb'] = float( self.economic_model_window.tv_shred.text() )
                
                # read user input Material Price Per lb data
                data.price_dict['aluminum_price'] = float( self.economic_model_window.al.text() )
                data.price_dict['copper_price'] = float( self.economic_model_window.cu.text() )
                data.price_dict['iron_price'] = float( self.economic_model_window.fe.text() )
                data.price_dict['plastic_price'] = float( self.economic_model_window.plastic.text() )
                data.price_dict['copper_yoke_price'] = float( self.economic_model_window.cu_yoke.text() )
                data.price_dict['degaussing_wire_price'] = float( self.economic_model_window.degaussing_wire.text() )
                data.price_dict['cd_rom_price'] = float( self.economic_model_window.cd_rom.text() )
                data.price_dict['power_sup_price'] = float( self.economic_model_window.power_supply.text() )
                data.price_dict['cpu_price'] = float( self.economic_model_window.cpu.text() )
                data.price_dict['ram_price'] = float( self.economic_model_window.ram.text() )
                data.price_dict['mixed_pc_wire_price'] = float( self.economic_model_window.mixed_pc_wire.text() )
                data.price_dict['silver_price'] = float( self.economic_model_window.ag.text() )
                data.price_dict['gold_price'] = float( self.economic_model_window.au.text() )
                data.price_dict['palladium_price'] = float( self.economic_model_window.pd.text() )
                environmental_fee_per_lb = float( self.economic_model_window.crt_tube_environmental_fee.text() )
                data.price_dict['environmental_fee_per_lb'] = [environmental_fee_per_lb, environmental_fee_per_lb, 0, 0, 0, 0, 0, 0, 0]
                
                
                
                # create economic model
                if self.economic_model_option_1:
                    em = EconomicModel(data, get_data_from_process_model = False)
                elif self.economic_model_option_2:
                    em = EconomicModel(data, get_data_from_process_model = True)    
                
                # run the model
                em.run_economic_model()
                
                # output text
                text = em.text
            
            except Exception as e: 
                text = f'{type(e).__name__}: {e.args}'
                
            
            self.economic_model_result_window.output.setText(text) 
            
            # create plot_window which is a instance of ShowPlot class
            self.plot_window = ShowEconomicPlot(em)
        
            # connect plot buttons
            self.economic_model_result_window.item_wise_plot_button.clicked.connect(self.plotItemWiseRevCostProfit)
            self.economic_model_result_window.overall_plot_button.clicked.connect(self.plotOverallRevCostProfit)
            
            # connect close buttons
            self.economic_model_result_window.close_btn.clicked.connect(self.economicModelResultCloseButton)

    def economicModelResultCloseButton(self):
        self.economic_model_window.show()  #show the process model window
        self.economic_model_result_window.close()
    
    def plotItemWiseRevCostProfit(self):
        self.plot_window.show()     #show the plot window
        self.plot_window.item_wise_cost_rev_profit() 
                
    def plotOverallRevCostProfit(self):
        self.plot_window.show()     #show the plot window
        self.plot_window.overall_cost_rev_profit()         


class ThreadClass_progress_bar_ws(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)
	
    def __init__(self, ws):
        super( ).__init__( )
        self.ws = ws
	
    def run(self):
        while (True):
            # time.sleep(0.01)
            QtTest.QTest.qWait(1)
            time_now = self.ws.env.now
            total_time = self.ws.sim_time
            percent_complete = int( round(time_now * 100 / total_time, 0) )            
            self.any_signal.emit(percent_complete)


class ThreadClass_WS(QtCore.QThread):
    # progress_value = QtCore.pyqtSignal(int) # or pyqtSignal(int)
	
    def __init__(self, bar, process_model_data, sim_time_data):
        super().__init__()
        # self.process_model_result_window = process_model_result_window
        self.bar = bar  # progress bar window; after finishing simulation we will enable 'show_result_btn'
               
        self.ws = Warehouse_simulation(process_model_data, sim_time_data)
	
    def run(self):        
        # run the simulation using run_simulation method
        self.ws.run_simulation()
        self.text = self.ws.text  # simulation statistics to show in the output window      
        self.bar.show_result_btn.setEnabled(True)
        
 

            
# process model window----------------------------------------------------------------------------------
class process_model_window(QMainWindow):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("process_model_input_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        
        # Set the output text Read Only mode
        # self.textEdit.setReadOnly(True)


# process model window----------------------------------------------------------------------------------
class Optimization_input_window(QMainWindow):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("optimization_input_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        

#  Economic model choice options window (independent run or get data from process model)--------------------------------
class ChooseEconomicModel(QDialog):    
    
    def __init__(self):
        super().__init__()
        loadUi("economic_model_choice_options.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        
# Economic model window 1 (independent run option) ---------------------------------------------------------------------
class Economic_model_window_1(QMainWindow):    
    
    def __init__(self):
        super().__init__()
        loadUi("economic_model_input_window_1.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        
        # Set the output text Read Only mode
        # self.textEdit.setReadOnly(True)

# Economic model window 2 get data from process model) ---------------------------------------------------------------------
class Economic_model_window_2(QMainWindow):    
    
    def __init__(self):
        super().__init__()
        loadUi("economic_model_input_window_2.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        
        # Set the output text Read Only mode
        # self.textEdit.setReadOnly(True)
        

# tool bar output window----------------------------------------------------------------------------------
# this output windoow is for tool bar output like about, user agreement etc.
class OutputWindow(QDialog):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("output_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # # Remove/disable the close button from the title bar
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        # add maximization button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # Set the output text Read Only mode
        self.output.setReadOnly(True)
        

# process model result window----------------------------------------------------------------------------------
class ProcessModelResultWindow(QDialog):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("result_process_model_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        # add maximization button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # Set the output text Read Only mode
        self.output.setReadOnly(True)
      

class ProgressBarWindow(QDialog):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("progress_bar.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)      


# economic model result window----------------------------------------------------------------------------------
class EconomicModelResultWindow(QDialog):    
    
    def __init__(self):
        super().__init__()
        loadUi("result_economic_model_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # Remove/disable the close button from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        # add maximization button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # Set the output text Read Only mode
        self.output.setReadOnly(True)




#  Transportation model choice options window (addressAdder or transportation model)--------------------------------
class ChooseTransportationModel(QDialog):    
    
    def __init__(self):
        super().__init__()
        loadUi("transportation_model_choice_options.ui", self)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)




# transportation model input window----------------------------------------------------------------------------------
class Transportation_input_window(QMainWindow):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("transportation_model_input_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # # Remove/disable the close button from the title bar
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)


# progress bar of transportation model
class ThreadClass_progress_bar_TM(QtCore.QThread):  #TM: Transportation Model
    any_signal = QtCore.pyqtSignal(int)
	
    def __init__(self, transport_model):
        super( ).__init__( )
        self.transport_model = transport_model
	
    def run(self):
        while (True):
            # time.sleep(0.01)
            QtTest.QTest.qWait(1)
            percent_complete = self.transport_model.progress       
            self.any_signal.emit(percent_complete)


# thread class where the transportation model will run
class ThreadClass_TM(QtCore.QThread):
	
    def __init__(self, bar,  df_od_matrix, df_collection_points, df_vehicles, df_unique_addresses, obj, weight_per_pallet_lbs):
        super().__init__()
        self.text = None
        # self.process_model_result_window = process_model_result_window
        self.bar = bar  # progress bar window; after finishing simulation we will enable 'show_result_btn'               
        
        self.transport_model = VRP(df_vehicles, df_od_matrix, df_collection_points, df_unique_addresses, obj, weight_per_pallet_lbs)

	
    def run(self):       
        # run the transport_model
        self.transport_model.run()
        self.text = self.transport_model.text
        # enable show_result_btn of the progress bar window
        self.bar.show_result_btn.setEnabled(True)


# transportation model result window----------------------------------------------------------------------------------
class TransportationModelResultWindow(QDialog):    
    
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("result_transportation_model_window.ui", self)
        
        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # # Remove/disable the close button from the title bar
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        # add maximization button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)

        
        # Set the output text Read Only mode
        self.output.setReadOnly(True)
                        
  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    # windows taskbar icon
    myappid = u'abcdef' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    #execute app
    app.exec_()
    # sys.exit(app.exec_())












