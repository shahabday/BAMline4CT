
from dataclasses import dataclass

#this object is created to store settings of the app 

@dataclass
class appSetting: 


    #EPICS channel Name : 
    epics_channel_name : str = "4DCT"
    
    volume_path_in_hdf : str = "/entry/data/data"
    angle_list_path_in_hdf : str = '/entry/instrument/NDAttributes/CT_MICOS_W'


