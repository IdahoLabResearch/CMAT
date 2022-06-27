# for addressAdder app
from PyQt5 import QtWidgets,uic
from configEdit_win import Ui_Dialog
import json


class DialogWindow(QtWidgets.QDialog):
    
    def __init__(self,parent):
        super(DialogWindow,self).__init__(parent)
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.initUI()
        self.readConfig()

    def initUI(self):
        self.ui.btnOK.clicked.connect(self.writeConfig)
        self.ui.btnCancel.clicked.connect(self.cancelAction)
        self.ui.btnBrowse.clicked.connect(self.browseFile)
    
    def readConfig(self):
        with open('config.json') as f:
            data=json.load(f)
            self.ui.txtApiKey.setText(data['API_KEY'])
            self.ui.txtStreet.setText(data['HOME_LOC']['Address'])
            self.ui.txtCity.setText(data['HOME_LOC']['City'])
            self.ui.txtCounty.setText(data['HOME_LOC']['County'])
            self.ui.txtState.setText(data['HOME_LOC']['State'])
            self.ui.txtPostCode.setText(data['HOME_LOC']['Postal Code'])
            self.ui.txtWorkDir.setText(data['WORKING_DIR'])

    def writeConfig(self):
        data={}
        data['API_KEY']=self.ui.txtApiKey.text()
        data['HOME_LOC']={
            'Address':self.ui.txtStreet.text(),
            'City':self.ui.txtCity.text(),
            'County':self.ui.txtCounty.text(),
            'State':self.ui.txtState.text(),
            'Postal Code':self.ui.txtPostCode.text()
        }
        data['WORKING_DIR']=self.ui.txtWorkDir.text()
        
        with open('config.json','w') as outfile:
            json.dump(data, outfile)
        self.close()

    def cancelAction(self):
        self.close()

    def browseFile(self):
        fName=QtWidgets.QFileDialog.getExistingDirectory(self,"Select Directory")
        self.ui.txtWorkDir.setText(fName)
