import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from mqtt_init import *

# Creating Client name - should be unique 
global clientname
r=random.randrange(1,100000)
clientname="IOT_client-Id-"+str(r)

class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic=''
        self.port='' 
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        
    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self,value):
        self.broker= value         
    def get_port(self):
        return self.port
    def set_port(self,value):
        self.port= value     
    def get_clientName(self):
        return self.clientName
    def set_clientName(self,value):
        self.clientName= value        
    def get_username(self):
        return self.username
    def set_username(self,value):
        self.username= value     
    def get_password(self):
        return self.password
    def set_password(self,value):
        self.password= value         
    def get_subscribeTopic(self):
        return self.subscribeTopic
    def set_subscribeTopic(self,value):
        self.subscribeTopic= value        
    def get_publishTopic(self):
        return self.publishTopic
    def set_publishTopic(self,value):
        self.publishTopic= value         
    def get_publishMessage(self):
        return self.publishMessage
    def set_publishMessage(self,value):
        self.publishMessage= value 
        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK")
            self.on_connected_to_form();            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)        
        print("Connecting to broker ",self.broker)        
        self.client.connect(self.broker,self.port)     #connect to broker
    
    def disconnect_from(self):
        self.client.disconnect()                   
    
    def start_listening(self):        
        self.client.loop_start()        
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):        
        self.client.subscribe(topic)
              
    def publish_to(self, topic, message):
        self.client.publish(topic,message)        
      
class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn=QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")
        

        self.MainMenu = MainMenuWindow()

        formLayot=QFormLayout()
        formLayot.addRow("Host",self.eHostInput )
        formLayot.addRow("Port",self.ePort )
        formLayot.addRow("Client ID", self.eClientID)
        formLayot.addRow("User Name",self.eUserName )
        formLayot.addRow("Password",self.ePassword )
        formLayot.addRow("Keep Alive",self.eKeepAlive )
        formLayot.addRow("SSL",self.eSSL )
        formLayot.addRow("Clean Session",self.eCleanSession )
        formLayot.addRow("",self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        self.MainMenu.show()
        mainwin.subscribeDock.connectToSensores()

            
class PublishDock(QDockWidget): ### Sprinkler Controller
    """Publisher """

    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc        
                
        self.ePublisherTopic=QLineEdit()
        self.ePublisherTopic.setText("irregation/sprinklerController")
        self.ePublisherTopic.setReadOnly(True) 

        #self.eQOS=QComboBox()
        #self.eQOS.addItems(["0","1","2"])

        self.eRetainCheckbox = QCheckBox()

        self.turnOnButton = QPushButton("Turn On",self)
        self.turnOnButton.clicked.connect(self.on_turnOnButton_click)


        self.turnOffButton = QPushButton("Turn Off",self)
        self.turnOffButton.setStyleSheet("background-color: red")
        self.turnOffButton.clicked.connect(self.on_turnOffButton_click)

        
        formLayot=QFormLayout()        
        formLayot.addRow("Topic",self.ePublisherTopic)
        #formLayot.addRow("QOS",self.eQOS)
        formLayot.addRow("Retain",self.eRetainCheckbox)
        formLayot.addRow("",self.turnOnButton)
        formLayot.addRow("",self.turnOffButton)
        
       
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget) 
        self.setWindowTitle("Sprinkler Controller")         
       
    def on_turnOnButton_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), "Turn On")
        self.turnOnButton.setStyleSheet("background-color: green")
        self.turnOffButton.setStyleSheet("background-color: gray")
    
    def on_turnOffButton_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), "Turn Off")
        self.turnOnButton.setStyleSheet("background-color: gray")
        self.turnOffButton.setStyleSheet("background-color:red")

        
class SubscribeDock(QDockWidget): ## Getting Params from Sensors
    """Subscribe """

    def __init__(self,mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        self.eSubscribeTopic=QLineEdit()
        self.eSubscribeTopic.setText("irregation/v1") 
        self.eSubscribeTopic.setReadOnly(True) 
        
        #self.eQOS = QComboBox()
       # self.eQOS.addItems(["0","1","2"])
        
        self.eRecMess=QTextEdit()
        self.eRecMess.setReadOnly(True)
        self.eRecMess.append("Waiting for Senseors repsone....")
        
        

        formLayot=QFormLayout()       
        formLayot.addRow("Topic",self.eSubscribeTopic)
        #formLayot.addRow("QOS",self.eQOS)
        formLayot.addRow("Received",self.eRecMess)
    
                
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget)
        self.setWindowTitle("Sensor Details")
        
        self.LastTemp = 0
        self.LastUV = 0


    def connectToSensores(self):
        print(self.eSubscribeTopic.text())
        self.mc.subscribe_to(self.eSubscribeTopic.text())
        mainwin.autoPilotDock.LastTempValue.setText(str(self.LastTemp))
        mainwin.autoPilotDock.LastUvValue.setText(str(self.LastUV))
        
    
    # create function that update text in received message window
    def update_mess_win(self,text):
        self.eRecMess.append(text)

        currentTxt = text.split(":")
        if(currentTxt[0] == "Temperature"):
            self.LastTemp = currentTxt[1]
            mainwin.autoPilotDock.LastTempValue.setText(self.LastTemp)
        else:
            self.LastUV = currentTxt[1]
            mainwin.autoPilotDock.LastUvValue.setText(self.LastUV)
        
        if(mainwin.autoPilotDock.IsAutoPilot == True):
            mainwin.autoPilotDock.CheckIfOptimalToTurnOnOrOff()

        
class MainWindow(QMainWindow): ### First Conection Menu
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 400, 200)
        self.setWindowTitle('Smart Irregation System')        

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)   
        self.publishDock =  PublishDock(self.mc)
        self.subscribeDock = SubscribeDock(self.mc)
        self.autoPilotDock = autoPilotWin()
        

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
       

class MainMenuWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

       
    # set up main window
        self.setGeometry(30, 100, 300, 200)
        self.setWindowTitle('Smart Irregation System Menu')  
        
        ### Move To Sensores Params Window
        self.sensParamsButt = QPushButton("See Sensoers Params",self)
        self.sensParamsButt.setGeometry(50,20,200,50)
        self.sensParamsButt.clicked.connect(self.on_button_MoveToParams)

        ### Move To Turn On/Off Sprinklers Window
        self.sprinkControlButt = QPushButton("Sprinkler Controler",self)
        self.sprinkControlButt.setGeometry(50,70,200,50)
        self.sprinkControlButt.clicked.connect(self.on_button_MoveToTurnSprinklerWin)

        #### Automate Sprinkler Controleer according to status
        self.autoPilotButt = QPushButton("Automate Controller",self)
        self.autoPilotButt.setGeometry(50,120,200,50)
        self.autoPilotButt.clicked.connect(self.on_button_AutoPilot)


    def on_button_MoveToParams(self):
        mainwin.subscribeDock.show()
    
    def on_button_MoveToTurnSprinklerWin(self):
        mainwin.autoPilotDock.IsAutoPilot = False
        mainwin.publishDock.show()

    def on_button_AutoPilot(self):
        mainwin.autoPilotDock.IsAutoPilot = True
        mainwin.autoPilotDock.show()
         

class autoPilotWin(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.IsAutoPilot = False

        self.setGeometry(30, 100, 300, 150)
        self.setWindowTitle('AutoPilot Controller') 

        self.tmpLabel = QLabel('Last Temp measured:', self)
        self.tmpLabel.setGeometry(20,0,150,50)

        self.LastTempValue = QLineEdit(self)
        self.LastTempValue.setGeometry(160,15,100,20)
        self.LastTempValue.setReadOnly(True)

        self.uvLabel = QLabel('Last UV measured:', self)
        self.uvLabel.setGeometry(20,45,150,20)

        self.LastUvValue = QLineEdit(self)
        self.LastUvValue.setGeometry(160,45,100,20)
        self.LastUvValue.setReadOnly(True)

        self.sprinklerStatus=QPushButton("", self)
        self.sprinklerStatus.setGeometry(120,80,60,20)
        self.sprinklerStatus.setStyleSheet("background-color: red")

    def CheckIfOptimalToTurnOnOrOff(self):
        if(self.LastTempValue.text() != '0' and self.LastUvValue.text() != '0'):
            if(int(self.LastUvValue.text()) <= 5 and float(self.LastTempValue.text()) <= 22.5):
                mainwin.publishDock.mc.publish_to("irregation/sprinklerController", "Turn On")
                self.sprinklerStatus.setStyleSheet("background-color: green")
            else:
                 mainwin.publishDock.mc.publish_to("irregation/sprinklerController", "Turn Off")
                 self.sprinklerStatus.setStyleSheet("background-color: red")
        

    



        
        



app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()

