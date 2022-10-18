import h5py
import numpy as np

def extract_3d_subvolume(file_path,ROI_initial,ROI_size):

    '''
    file_path :   string file path to the hdf file 
    ROI_initial   :   z,y,x  coordination of the initial point in the volume for ROI
    ROI_size      :   h,w,l  height , width and length of the ROI 
    
    '''
    #debugging : 

    #possible problems are : 
    #1. ROI_initial, ROI_size , are not in form of slicable variable with three values
    #2. the hdf file has no data under selected name (here , Volume )
    #3. ROI_initial, ROI_size are not intigers 

    z,y,x = ROI_initial
    h,w,l = ROI_size


    with h5py.File(file_path, 'r')  as f :
            vol_proxy = f['Volume']
            extracted_volume = vol_proxy[z:z+h,y:y+w,x:x+l]
            

    return extracted_volume


def extract_slices (volume,slice, axis= 1):

    '''
    volume is a numpy array in format : (z,y,x) ??? 
    axis is an int. 0 for first axis, 1 for the second and 2 for the thrid axis 
    slice is an int and indicates which slice we want to extract
    
    '''
    #debugging: 
    #possible problems :
    #1. invalid axis is selected.
    #2. selected slice number is out of range
    
    the2Dslice = volume.take(indices=slice, axis=axis)
        
    

    return the2Dslice

