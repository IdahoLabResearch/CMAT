from PyQt5 import QtWidgets, QtCore, QtGui,uic
from mainform_win import Ui_MainWindow
import json
import csv
import requests
import configEdit
from os.path import exists

class AddressAdder(QtWidgets.QMainWindow):
    def __init__(self):
        super(AddressAdder,self).__init__()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.readConfig()
        self.records=[]
        self.initUi()
        self.show()

    def initUi(self):
        # Add File Menu Item
        self.fileMenu=self.ui.menubar.addMenu('File')

        ## Add File Submenu Items
        self.openAction=QtWidgets.QAction('Load File')
        self.newAction=QtWidgets.QAction('New')
        self.saveAction=QtWidgets.QAction('Save')
        self.editAction=QtWidgets.QAction('Edit Config File')
        self.closeAction=QtWidgets.QAction('Close')
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.editAction)
        self.fileMenu.addAction(self.closeAction)
        self.openAction.triggered.connect(self.loadFile)
        self.newAction.triggered.connect(self.newFile)
        self.saveAction.triggered.connect(self.saveRecords)
        self.editAction.triggered.connect(self.editConfig)
        
        
        ##Button Funcionality
        self.ui.btnBrowse.clicked.connect(self.loadFile)
        self.ui.btnSave.clicked.connect(self.saveRecords)
        self.ui.btnCancel.clicked.connect(self.resetTxtBoxValues)


    def readConfig(self):
        with open('config.json') as f:
            data=json.load(f)
            self.API_KEY=data['API_KEY']
            self.HOME_ADDRESS=data['HOME_LOC']['Address']
            self.HOME_CITY=data['HOME_LOC']['City']
            self.HOME_COUNTY=data['HOME_LOC']['County']
            self.HOME_STATE=data['HOME_LOC']['State']
            self.HOME_POST_CODE=data['HOME_LOC']['Postal Code']
            self.WORKING_DIR=data['WORKING_DIR']

    def newFile(self):
        fName=QtWidgets.QFileDialog.getSaveFileName(self,'Save File', self.WORKING_DIR,"CSV files (*.csv)")
        self.ui.txtLoadedFile.setText(fName[0])

    def loadFile(self):
        fName=QtWidgets.QFileDialog.getOpenFileName(self,'Load File', self.WORKING_DIR, "CSV files (*.csv)")
        self.ui.txtLoadedFile.setText(fName[0])

    def editConfig(self):
        dlg=configEdit.DialogWindow(self)
        dlg.exec_()

    def addAccount(self):
        if not self.ui.txtLoadedFile.text()=='':
            record={}
            if not exists(self.ui.txtLoadedFile.text()) and len(self.records)==0:
                self.records.append({
                    'acctId':0,
                    'acctName':'HOME',
                    'clientType':'N/A',
                    'acctOwner':'N/A',
                    'address':self.HOME_ADDRESS,
                    'city':self.HOME_CITY,
                    'county':self.HOME_COUNTY,
                    'state':self.HOME_STATE,
                    'postCode':self.HOME_POST_CODE
                })
            if self.validateInputs():
                record['acctId']=self.ui.txtAcctID.text()
                record['acctName']=self.ui.txtAcctName.text()
                record['clientType']=self.ui.txtClientType.text()
                record['acctOwner']=self.ui.txtAcctOwner.text()
                record['address']=self.ui.txtAddress.text()
                record['city']=self.ui.txtCity.text()
                record['county']=self.ui.txtCounty.text()
                record['state']=self.ui.txtState.text()
                record['postCode']=self.ui.txtPostalCode.text()
                self.records.append(record)
                self.resetTxtBoxValues()
        else:
            raise Exception("Must have file path specified by either loading an existing file or creating a new file")

    def saveRecords(self):
        def replaceSpaces(string):
            vals=string.split(' ')
            loops=len(vals)-1
            outstring=vals[0]
            i=0
            while i < loops:
                outstring+=f'%20{vals[i+1]}'
                i+=1 
            return outstring

        def geocodeAddress(record):
            street_number,route=record['address'].split(' ',1)
            city=record['city']
            state=record['state']
            post=record['postCode']
            fmt_address=f'{street_number}%20{replaceSpaces(route)}%20{replaceSpaces(city)}%20{state}%20{post}'
            geocode_url=f'https://maps.googleapis.com/maps/api/geocode/json?address={fmt_address}&key={self.API_KEY}'

            response=requests.request('GET',geocode_url)
            coords=response.json()['results'][0]['geometry']['location']
            lat=coords['lat']
            lng=coords['lng']
            return lat,lng

        def calcDistMatrix(coords):
            i=0
            matrix=[]
            if not exists(f'{self.ui.txtLoadedFile.text()[:-4]}_OD.csv'):
                origin=''
                dests=''
                while i<len(coords)-1:
                    origin+=f'{coords[i][-2]}%2C{coords[i][-1]}'
                    j=i+1
                    while j<len(coords):
                        dests+=f'{coords[j][-2]}%2C{coords[j][-1]}'
                        url= f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={dests}&key={self.API_KEY}'
                        response=requests.request("GET",url)
                        dist=(response.json()['rows'][0]['elements'][0]['distance']['value'])/1609.34
                        time=(response.json()['rows'][0]['elements'][0]['duration']['value'])/3600
                        matrix.append([f'{i}-{j}',time,dist])
                        j+=1
                    i+=1
                with open(f'{self.ui.txtLoadedFile.text()[:-4]}_OD.csv','w',newline='') as f:
                        writer=csv.writer(f)
                        writer.writerow(['idx','time','distance'])
                        writer.writerows(matrix)
            else:
                for c in coords:  
                    with open(f'{self.ui.txtLoadedFile.text()[:-4]}_Unique.csv','r') as prev:
                        reader=csv.reader(prev)
                        next(reader)
                        for r in reader:
                            dests=f'{c[-2]}%2C{c[-1]}'
                            origin=f'{r[-2]}%2C{r[-1]}'
                            url= f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={dests}&key={self.API_KEY}'
                            response=requests.request("GET",url)
                            dist=(response.json()['rows'][0]['elements'][0]['distance']['value'])/1609.34
                            time=(response.json()['rows'][0]['elements'][0]['duration']['value'])/3600
                            matrix.append([f'{r[0]}-{c[0]}',time,dist])
                    with open(f'{self.ui.txtLoadedFile.text()[:-4]}_OD.csv','a',newline='') as f:
                        writer=csv.writer(f)
                        writer.writerows(matrix)

        i=0
        accounts=[]
        coords=[]
        self.addAccount()
        if exists(self.ui.txtLoadedFile.text()):
            with open(self.ui.txtLoadedFile.text()) as file:
                reader = csv.reader(file)
                lines=len(list(reader))
                i=lines-1
        for r in self.records:
            row=[
                r['acctId'],
                r['acctName'],
                r['clientType'],
                r['acctOwner'],
                r['address'],
                r['city'],
                r['county'],
                r['state'],
                r['postCode']
                ]
            accounts.append(row)
            lat,lng=geocodeAddress(r)
            coord=[i,r['acctId'],r['acctName'],f'{r["address"]},{r["city"]},{r["state"]}',lat,lng]
            coords.append(coord)
            i+=1
        self.writeFiles(self.ui.txtLoadedFile.text(),['Account ID','Account Name','Client Type','Account Owner', 'Address','City','County','State','Postal Code'],accounts)   
        calcDistMatrix(coords)
        self.writeFiles(f'{self.ui.txtLoadedFile.text()[:-4]}_Unique.csv',['Index','Account ID', 'Account Name', 'Address','Lat','Lng'],coords) 
        self.records=[]

    def validateInputs(self):
        retVal=True
        if (
            self.ui.txtAcctID.text()=='' and
            self.ui.txtAcctName.text()=='' and
            self.ui.txtClientType.text()=='' and
            self.ui.txtAcctOwner.text()=='' and
            self.ui.txtAddress.text()=='' and
            self.ui.txtCity.text()=='' and 
            self.ui.txtCounty.text()=='' and 
            self.ui.txtState.text()=='' and 
            self.ui.txtPostalCode.text()==''
            ):
            retVal=False
        return retVal

    def resetTxtBoxValues(self):
        self.ui.txtAcctID.setText('')
        self.ui.txtAcctName.setText('')
        self.ui.txtClientType.setText('')
        self.ui.txtAcctOwner.setText('')
        self.ui.txtAddress.setText('')
        self.ui.txtCity.setText('')
        self.ui.txtCounty.setText('') 
        self.ui.txtState.setText('') 
        self.ui.txtPostalCode.setText('')
    
    def writeFiles(self,filePath,headers,data):
        if exists(filePath):
            with open(filePath,'a',newline='') as f:
                writer=csv.writer(f)
                writer.writerows(data)
        else:
            with open(filePath,'w',newline='') as f:
                writer=csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)