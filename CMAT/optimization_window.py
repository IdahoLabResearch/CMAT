from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QMenuBar
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtTest
from PyQt5.QtGui import QCursor, QIcon, QFont
from manpower_optimization import Optimization

import sys
import ctypes


class OptimizationInputWindow(QMainWindow):

    def __init__(self):
        """MainWindow constructor."""
        super(OptimizationInputWindow, self).__init__()
        self.ui = loadUi("manpower_optimization_input_window.ui", self)
        self.show()
        self.thread={}


        ##Button Funcionality
        self.ui.run_btn.clicked.connect(self.run_optimization)
        self.ui.browse_btn.clicked.connect(self.browseFile)

        # change mouse icon when hover over buttons
        button_list = [self.ui.browse_btn, self.ui.run_btn, self.ui.back_btn]
        for button in button_list:
            button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))


    # for process and economic model
    def browseFile(self):
        fileNameTuple = QFileDialog.getOpenFileName(self, 'OpenFile',"", "(*.xls *.xlsx *.csv)")
        fileName = fileNameTuple[0]
        self.file_name = fileName
        # show the file name in QLineEdit box
        file_name_with_path = self.file_name.split("/")
        excel_file_name = f'{file_name_with_path[0]}\ .. \{file_name_with_path[-1]}'
        self.ui.selected_file_box.setText(excel_file_name)


    def run_optimization(self):
        # output window for optimization output
        self.optimization_model_result_window = OutputWindow()
        self.optimization_model_result_window.hide()  #show the output window
        self.hide()  #hide the process model input window

        energy_cost_per_kwh        = float( self.ui.energy_cost_per_kwh.text() )
        available_operators        = self.ui.spin_box_available_operators.value()
        weeks                      = self.ui.spin_box_weeks.value()
        days                       = self.ui.spin_box_days.value()
        shifts                     = self.ui.spin_box_shifts.value()
        hours                      = self.ui.spin_box_hours.value()

        population                 = self.ui.spin_box_population_size.value()
        max_iteration              = self.ui.spin_box_maximum_iteration.value()
        max_run_time               = self.ui.spin_box_max_optimization_time.value()

        self.bar = ProgressBarWindow()
        self.bar.show()
        self.thread[1] = ThreadClass_Optimization(self.bar, energy_cost_per_kwh, available_operators, weeks, days, shifts, hours, self.file_name, population, max_iteration, max_run_time)
        self.thread[1].start()
        print(self.thread[1].optimization_model.text)

        self.bar.show_result_btn.setEnabled(False)
        self.bar.show_result_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.thread[2] = ThreadClass_progress_bar(self.thread[1].optimization_model)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.updateProgressBar)

        # connect buttons
        self.optimization_model_result_window.close_button.clicked.connect(self.optimizationModelResultCloseButton)
        self.bar.show_result_btn.clicked.connect(self.show_optimization_results)



    def updateProgressBar(self, value):
        if value == True:
            self.bar.qLabel_message.setText("Complete!!! Click the below button to see results")

    def show_optimization_results(self):
        self.optimization_model_result_window.show()
        self.optimization_model_result_window.output.setText(self.thread[1].optimization_model.text)
        # set window title
        self.optimization_model_result_window.setWindowTitle('Output')
        self.bar.close()

    def optimizationModelResultCloseButton(self):
        self.show()  #show the process model window
        self.optimization_model_result_window.close()

        # close the threads
        try:
            self.thread[1].terminate()
            self.thread[2].terminate()
        except:
            pass


# thread class where the transportation model will run
class ThreadClass_Optimization(QtCore.QThread):

    def __init__(self, bar, energy_cost_per_kwh, available_operators, weeks, days, shifts, hours, file_name, population, max_iteration, max_run_time):
        super().__init__()
        self.bar = bar  # progress bar window; after finishing simulation we will enable 'show_result_btn'
        self.optimization_model = Optimization(energy_cost_per_kwh, available_operators, weeks, days, shifts, hours, file_name, population, max_iteration, max_run_time)


    def run(self):
        # run the transport_model
        self.optimization_model.run_HACO()
        self.text = self.optimization_model.text

        # enable show_result_btn of the progress bar window
        self.bar.show_result_btn.setEnabled(True)
        self.bar.qLabel_message.setText("Complete!!! Click the below button to see results")


class ThreadClass_progress_bar(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(bool)

    def __init__(self, optimization_model):
        super( ).__init__( )
        self.optimization_model = optimization_model

    def run(self):
        while (True):
            # time.sleep(0.01)
            QtTest.QTest.qWait(1)
            optimization_complete = self.optimization_model.optimization_complete # True or False
            self.any_signal.emit(optimization_complete)

class ProgressBarWindow(QDialog):

    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        loadUi("optimization_progress.ui", self)

        # Make the window size fixed
        # self.setFixedSize(600, 576)

        # Remove the ? mark from the title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)


# this output windoow is for optimization result output
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = OptimizationInputWindow()
    w.show()
    # windows taskbar icon
    myappid = u'abcdef' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    #execute app
    app.exec_()
    # sys.exit(app.exec_())
