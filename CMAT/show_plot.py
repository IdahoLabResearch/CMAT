
import sys
import os
from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QMainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np


# set plot style
# plt.style.use('seaborn')
plt.style.use('my_style.mplstyle')


class ShowProcessPlot(QDialog):
    def __init__(self, ws, parent=None):
        super(ShowProcessPlot, self).__init__(parent)
        self.ws = ws

        # a figure instance to plot on
        self.figure = plt.figure(constrained_layout=True,  dpi = 100, figsize =(10,5))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        

        # # this is the Navigation widget
        # # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)


        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # add maximize window button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # set the title
        self.setWindowTitle('Plot')

    def plot_utilization_storage_area(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
 
        plt.figure(dpi = 300, figsize =(8, 5), constrained_layout=True ) 
        
        for process in self.ws.processes:
            if type(process).__name__ in ['ContinuousStorage', 'UnitStorage']:
                # if process.name != 'Residential FIFO':
                y = process.capacity_utilization_history
                x = range(len(y))
                ax.plot(x, y, label = f'{process.name}')
    
        ax.set_xlabel('Time (minutes)', fontweight = 'bold')
        ax.set_ylabel('Utilization (%)', fontweight = 'bold')    
        ax.legend()
        ax.set_title('Storage Area Capacity Utilization', fontweight = 'bold')

        # refresh canvas
        self.canvas.draw()
        
    def plot_utilization_shredding_stations(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
 
        plt.figure(dpi = 300, figsize =(8, 5), constrained_layout=True ) 
        
        for process in self.ws.processes:
            if type(process).__name__ in ['Machine']:
                y = process.capacity_utilization_history
                x = range(len(y))
                ax.plot(x, y, label = f'{process.name}')
    
        ax.set_xlabel('Time (minutes)', fontweight = 'bold')
        ax.set_ylabel('Utilization (%)', fontweight = 'bold')
        ax.legend()
        ax.set_title('Processing Capacity Utilization of Shredding Stations', fontweight = 'bold')

        # refresh canvas
        self.canvas.draw()

    def plot_utilization_manual_work_station(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
 
        plt.figure(dpi = 300, figsize =(8, 5), constrained_layout=True ) 
        
        for process in self.ws.processes:
            if type(process).__name__ in ['Manual_work_station', 'Dismantling_station']:
                y = process.capacity_utilization_history
                x = range(len(y))
                ax.plot(x, y, label = f'{process.name}')
        
        ax.set_xlabel('Time (minutes)', fontweight = 'bold')
        ax.set_ylabel('Utilization (%)', fontweight = 'bold')
        ax.legend() 
        ax.set_title('Capacity Utilization of Manual Workstations', fontweight = 'bold')

        # refresh canvas
        self.canvas.draw()
        
        
    def plot_output(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
 
        plt.figure(dpi = 300, figsize =(8, 5), constrained_layout=True ) 
 
        x = []
        y = []
        for process in self.ws.processes:
            if type(process).__name__ in ['Manual_work_station', 'Dismantling_station', 'Machine']:
                x.append(process.name)
                y.append(process.total_output_mass)
    
        b = ax.bar(x, y, width = 0.3, alpha = 0.5)
        ax.set_ylabel('Output (lbs)', fontweight = 'bold')
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
        ax.set_xticklabels(labels=x, rotation=45, ha='right', fontweight = 'bold')
        ax.set_title('Output of Different Workstations', fontweight='bold')
        
        # define a function for auto labeling
        def auto_label(ax, bars):
            """
            Attach a text label above each bar displaying its height
            """
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, 0.00*height,
                        f'{height : ,.0f}',
                        ha='center', va='bottom',
                        rotation=90, color = 'k', fontsize=14, fontweight = 'bold')
        
        auto_label(ax, b)

        # refresh canvas
        self.canvas.draw()
 
    def plot_ctegory_wise_processing_cost(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
 
        plt.figure(dpi = 300, figsize =(8, 5), constrained_layout=True ) 
 
        x = ['CRT TV', 'CRT Monitor', 'LCD TV', 'LCD Monitor', 'Desktop', 'Laptop', 'Printer', 'Small CEE', 'Computer Peripherals']
        y = self.ws.item_wise_processing_cost_per_lb 
        b = ax.bar(x, y, width = 0.3, alpha = 0.5)
        
        ax.set_ylabel('$/lb', fontweight = 'bold')
        ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.2f}'))
        ax.set_xticklabels(labels=x, rotation=45, ha='right', fontweight = 'bold') 
        ax.set_title('Processing Cost (Without Overhead)', fontweight='bold')
        
        # define a function for auto labeling
        def auto_label(ax, bars):
            """
            Attach a text label above each bar displaying its height
            """
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, 0.00*height,
                        f'{height : ,.2f}',
                        ha='center', va='bottom',
                        rotation=90, color = 'k', fontsize=14, fontweight = 'bold')
        
        auto_label(ax, b)

        # refresh canvas
        self.canvas.draw()

      
        
#%%
class ShowEconomicPlot(QDialog):
    def __init__(self, em, parent=None):
        super(ShowEconomicPlot, self).__init__(parent)
        self.em = em  # em: economic model

        # a figure instance to plot on
        self.figure = plt.figure(constrained_layout=True,  dpi = 100, figsize =(10, 5))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        

        # # this is the Navigation widget
        # # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)


        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # add maximize window button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # set the title
        self.setWindowTitle('Plot')
    
    
    def item_wise_cost_rev_profit(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])
        
        revenue = self.em.revenue_per_lb_item_wise
        cost = self.em.processing_cost_per_lb_item_wise
        profit = self.em.profit_per_lb_item_wise
        
        
       
        labels = ['CRT TV', 'CRT Monitor', 'LCD TV', 'LCD Monitor', 'Desktop', 'Laptop', 'Printer', 'Small CEE', 'Computer Peripherals']
        x = np.arange(len(labels))  # X tick label locations
        width = 0.25  # the width of the bars
        color = ['deepskyblue', 'orangered', 'orange',]
        
        b1 = ax.bar(x - 1*width, revenue, width = width, color = color[0], alpha = 1.0, label='Revenue')
        b2 = ax.bar(x + 0*width, cost, width = width, color = color[1], alpha = 1.0, label='Processing Cost')
        b3 = ax.bar(x + 1*width, profit, width = width, color = color[2], alpha = 1.0, label='Profit')
        
        ax.set_ylabel('$/lb', fontweight = 'bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels=labels, rotation=45, ha='right', fontweight = 'bold', fontsize=12)
        ax.legend(bbox_to_anchor=(0.00, 1.15), loc='upper left', ncol=3, fontsize=13)
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
                        f'{height : .2f}',
                        ha='center', va='bottom',
                        rotation=90, color = 'k', fontsize=12, fontweight = 'bold') 
                
        auto_label(ax, b1)
        auto_label(ax, b2)
        auto_label(ax, b3)

        # refresh canvas
        self.canvas.draw()          

    def overall_cost_rev_profit(self):
        # clear the figure
        self.figure.clear()
        
        # create an axis
        gs = GridSpec(1, 1, figure=self.figure)
        ax = self.figure.add_subplot(gs[0, 0])

        x = ['Overall Revenue', 'Overall Cost', 'Overall Profit',]
        # x = np.arange(len(labels))  # X tick label locations
        y = [self.em.revenue_per_lb_overall,
             self.em.overall_processing_cost_per_lb,
             self.em.profit_per_lb_overall
             ]
        
        width = 0.25  # the width of the bars  
        
        b = ax.bar(x, y, width = width, color = 'dodgerblue', alpha = 1.0)
        ax.set_ylabel('$/lb', fontweight = 'bold', fontsize=12)
        ax.set_xticklabels(labels=x, rotation=0, ha='center', fontweight = 'bold', fontsize=12)
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
                        f'{height : .2f}',
                        ha='center', va='bottom',
                        rotation=90, color = 'k', fontsize=12, fontweight = 'bold') 
                
        auto_label(ax, b)
        
        
        # refresh canvas
        self.canvas.draw() 
        

#%%
class ShowTransportationPlot(QDialog):
    def __init__(self, file_path, parent=None):
        super(ShowTransportationPlot, self).__init__(parent)
        
        # self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.webEngineView = QtWebEngineWidgets.QWebEngineView()
        # self.webEngineView.load(QtCore.QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]+r'\Route_map.html'))
        file_path = file_path + r'Route_map.html'
        self.webEngineView.load(QtCore.QUrl().fromLocalFile(file_path))

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.webEngineView)
        self.setLayout(layout)
        
        self.resize(1500, 800)

        # Remove the ? mark from the title bar        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # add maximize window button
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinMaxButtonsHint)
        
        # set the title
        self.setWindowTitle('Transportation Model Map')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    from economic_model import EconomicData, EconomicModel
    # create data
    data = EconomicData(excel_file_name = 'economic model data.xlsx')    
    # create economic model
    em = EconomicModel(data)
    # run the model
    em.run_economic_model()
    
    main = ShowEconomicPlot(em)
    main.item_wise_cost_rev_profit()
    # main.overall_cost_rev_profit()
    # main = ShowTransportationPlot('C:\\Users\\RAHMM\\Desktop\\REMADE\\')
    main.show()

    sys.exit(app.exec_())
    
      
  

