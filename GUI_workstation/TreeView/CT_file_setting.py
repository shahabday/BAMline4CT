from dataclasses import dataclass

# this file dictates the structure of a CT file 
# this helps storing the data and settings required for reconstruction of 
# either a slice, or the whole volume

# for a batch reconstruction or 4D reconstruction, this comes in very handy
# since all information subject to change while user is adjusting the parameters


@dataclass
class CT_file_setting:
    #projection file data : 
    file_name : str
    # if you need you can have a random generated id :
    #  

    # the selected CT_files , will be passed to the final reconstruction module 
    selected : bool = False # this is to see if it is selected for CT reconstruction or not 

    angle_list_dir : str  ='/entry/instrument/NDAttributes/CT_MICOS_W'# path in HDF5 file where angle list are stored
    number_of_FFs :int  = 20 # this is needed in other functions 
    DarkFieldValue : int = 200# this is needed in other functions 
    backIlluminationValue : int  = 0# this is needed in other functions 

    #reconstruction settings :

    COR : float = 1228
    Offset_Angle : float = 0 
    reco_algorithm : str  = "gridrec"
    filter_name : str   ="shepp"
    n_cores : int = 16
    block_size  : int  = 60
    pixel_size : float = 0.72
    GPU : bool = False 

    #save_settings  : 
    
    dtype : str = "float32"# or float32
    fileType : str  =  "tif"
    chunking : tuple = None
    save_folder : str = "D:\\shahab\\HDF\\Writer\\{}"

    # default value appear here : 
    
if __name__ == "__main__":
    ct1 = CT_file(file_name = "CT1"  , COR= 1222)
    ct1.COR = 40
    print (ct1)
    cts = []

    for i in range (4) : 
        ct_i = CT_file(file_name = "CT{}".format(i)  , COR= 1222)
        cts.append(ct_i)

    #print (cts)

    for attr, value in ct1.__dict__.items():
        print(attr, value )
