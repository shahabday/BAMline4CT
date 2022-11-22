from dataclasses import dataclass

# this file dictates the structure of a CT file 
# this helps storing the data and settings required for reconstruction of 
# either a slice, or the whole volume

# for a batch reconstruction or 4D reconstruction, this comes in very handy
# since all information subject to change while user is adjusting the parameters

# some values will be field upon opening the hdf file :
# these vlaues are depending on the import setting and save setting files 
# other values will not be pre-filled and will be given None : 
# this is not to mess up default values in the reco Parameter window. 
# when recieved for the first time, reco Parameter widget checks the values, 
# if they are given None, it will not update the fields in the widget. 

@dataclass
class CT_file_setting:
    #projection file data : 
    file_name : str
    # if you need you can have a random generated id :
    #  filename acts as a unique ID 
    folder_name : str

    # the selected CT_files , will be passed to the final reconstruction module 
    selected : bool = False # this is to see if it is selected for CT reconstruction or not 

    angle_list_dir : str  = '/entry/instrument/NDAttributes/CT_MICOS_W'# path in HDF5 file where angle list are stored
    number_of_FFs :int  = None # this is needed in other functions 
    DarkFieldValue : int = None# this is needed in other functions 
    backIlluminationValue : int  = None# this is needed in other functions 

    #reconstruction settings :
    slice_number : int = None
    COR : float = None
    offset_Angle : float = None 
    ring_radius : int = None
    speed_w : float = None
    reco_algorithm : str  = None
    filter_name : str   =None
    n_cores : int = 16
    block_size  : int  = 60
    pixel_size : float = None
    GPU : bool = False 

    #phase contrast settings: 
    

    #save_settings  : 
    
    dtype : str = "float32"# or float32
    fileType : str  =  None

    chunking_x : int = None
    chunking_y : int = None 
    intensity_low : float = None
    intensity_high : float = None
    save_folder : str = None 
    first_slice : int = None
    last_slice : int   = None 
    
    
    
   

    @property
    def chunking(self):
        "this is a getter method"
        return (1,self.chunking_x , self.chunking_y)
 
    @chunking.setter
    def chunking(self, value):
        "this is a setter method"
        self.chunking = value

    @property
    def slice_range(self):
        "this is a getter method"
        return (self.first_slice , self.last_slice)
    
    @slice_range.setter
    def slice_range(self, value):
        "this a setter method"
        self.slice_range = value


    def update(self , val_dict):
        # val_dict : a dictionarty containing new values 
        for key, value in val_dict.items():
            if hasattr(self,key):
                setattr(self,key,value)

    def get_values ( self, attr_list ) : 
        # attr_list : a list of requested values 
        values ={}
        
        for attr in attr_list : 
            #getting methode : 
            value = getattr(self,attr)
            values[attr] = value
        return values 





    
if __name__ == "__main__":
    ct1 = CT_file_setting(file_name = "CT1"  , COR= 1222 , folder_name="sahl")
    ct1.COR = 40

    print(ct1.get_values(["chunking","reco_algorithm","COR"]))
    #ret_dic = ct1.get_values(["COR","chunking", "angle_list_dir" , "selected"])
    #ch_func = ret_dic["chunking"]
    #print (ct1.get_values(["chunking","reco_algorithm","COR"]))
    #print(ch_func.__get__())
  

    """
    print (ct1.get_values(["angle_list_dir" , "selected"]))
    print (ct1.chunking)
    ct1.chunking_x = 200 
    print(ct1.chunking)
    ct1.last_slice = 500
    print(ct1.slice_range)
    print (ct1.get_values(["chunking","reco_algorithm","COR"]))

    """
    #print(ct1.get_val)