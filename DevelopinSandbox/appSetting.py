
from dataclasses import dataclass

#this object is created to store settings of the app 

@dataclass
class appSetting: 


    #EPICS channel Name : 
    epics_channel_name : str = "4DCT"


