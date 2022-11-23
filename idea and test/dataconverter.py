
"""
This is a series of functions to easily convert older datasets measured in BAMline to the new versions

dataset version from 2021 12  is converted to new dataset format 


new Version has the following format : 

entry/data/data : dataset of projections with shape (number_of_projections, heigt ,width )

entry/instrument/NDAttributes/CT-MiCOS_W : data set of rotation angles with shape (number_of_projections)

Flat fields are written in the begginning and end of the dataset .

the older version (2021-12) has the following format 

we have many single hdf5 files. in each the data is written : 
entry/data/data :   Image projection (heigt ,width )
entry/instrument/NDAttributes/CT-MiCOS_W : (1)


"""


import h5py
import os
import tifffile


def get_file_counter(fullPath,number_of_digits):

    filename=os.path.splitext(os.path.basename(fullPath))[0]
    counter = filename[-number_of_digits:]
    counter = int(counter)
    return counter

def get_file_extension (fullPath):
    _, file_extension = os.path.splitext(fullPath)
    return file_extension


def create_file_dic (path_folder ,file_extension,number_of_digits):

    """
    This function gets a folder path , looks for all h5 files in the folder . 
    the h5 files are supposed to be numbered as  : 
    Files are written like this : 
    XYXYUYU_00001.h5   a 5-digit nummber is before h5

    return : a dict = {filenumber : full file path to the file  }
    
    """
    all_files =  os.listdir(path_folder)
    all_files = [ os.path.join(path_folder,file) for file in all_files]
    file_dic = {}
    for file in all_files:
        if get_file_extension(file) == file_extension:
            file_dic[get_file_counter(file,number_of_digits)] = file
            #file_list.append([get_file_counter(file) , file])
            #file_list : [[counter, file_path]]
    return file_dic




   
def createFolder(pathFolder):

    if not os.path.exists(pathFolder):
        os.makedirs(pathFolder)

def createdataset(f, dataset_path, data):
    if data.ndim == 3 :#must feed shape (1,n,m)
        f.create_dataset(dataset_path, data = data , maxshape=(None, data.shape[1], data.shape[2]),chunks = True)
    elif data.ndim == 1 : # if data was one dimension 
        f.create_dataset(dataset_path, data = data , maxshape=(None,),chunks = True)


def write_to_hdf(data,dataset_path,fname,path_to_write):

    """
    # Write data into a new or an existing hdf file 

    you can use this functino to create or write incrementally datasets in a hdf5 file 

    datasets could be 1D,  2D or  3D
    
    
    
    """

    hdf5_fullpath = os.path.join(path_to_write,fname)
    _, file_extension = os.path.splitext(hdf5_fullpath)
    if file_extension != ".h5" : 
        print("the hdf5 file extension is not correct")
        fname = fname + ".h5"
        hdf5_fullpath = os.path.join(path_to_write,fname)
    createFolder(path_to_write)

    #convert 2D projection to 3D with (1,n,m)
    if data.ndim ==2 : 
        data = data.reshape(1,data.shape[0],data.shape[1])
    
    #check if hdf file already exists : 
    if not os.path.exists(hdf5_fullpath) :
        #create hdf file if does not exist
        with h5py.File(hdf5_fullpath , 'w') as f : 
            createdataset(f,dataset_path, data)
    else:
    #if exists, fill in the volume 
        #open h5 file 
        f = h5py.File(hdf5_fullpath,"r+")
        #check if dataset exists : 
        if dataset_path in f : 
            print("it exists it exists filling it ")
            data_proxy = f[dataset_path]
            shape = data_proxy.shape
            print(shape)
            print(data.shape)

            if data.ndim == 3 :
                

                data_proxy.resize((shape[0] + data.shape[0]), axis=0)

                data_proxy[shape[0] : shape[0] + data.shape[0] ,:,:] = data

            if data.ndim == 1 : 
                data_proxy.resize((shape[0] + data.shape[0]), axis=0)

                data_proxy[shape[0] : shape[0] + data.shape[0] ] = data

            #close file
            f.close()
        else :
            createdataset(f,dataset_path,data)
            f.close()
            
def convert_ (path_old_file , extract_dic , path_new_file, new_file_name):
    
    file_dic = create_file_dic(path_old_file)
    # 1D data to extract : 
    # extract_dic["1D_data_path"] is a list of path to all 1D data we wish to extract
    
   

    for index in range (1,len(file_dic)):
        #for index in range (1,100):
        
        #read data from the h5 file 
        f = h5py.File(file_dic[index], "r")
        for one_d_data  in extract_dic["1D_data_path"] :
            onedData = f[one_d_data]
            _data = onedData[:]
            write_to_hdf(_data,one_d_data,new_file_name,path_new_file)
        data_path = extract_dic["Projectein_data_path"]
        projection_proxy = f[data_path]
        projection =projection_proxy[:]
        
        write_to_hdf(projection,data_path,new_file_name,path_new_file)

        f.close()


    

if __name__ == '__main__':
    #Test 1 : 
    import numpy as np 

    test = 6


    if test== 6 : 

        # conversion of data recorded as tiff but as on-the-flz mode. without any metadata . Version 2021 10

        # data are stored in this folder  :A:\BAMline-CT\2021\2021_10\Markoetter
        # but not all are needed to be converted 

        folder_old = r"A:\BAMline-CT\2021\2021_10\Markoetter"
        dir_list  = os.listdir(r"A:\BAMline-CT\2021\2021_10\Markoetter")
        dir_list = [dir for dir in dir_list if os.path.isdir(os.path.join(r"A:\BAMline-CT\2021\2021_10\Markoetter",dir))]

        selected_folder_index = [28,29,30,32,36,37,38,39,41,43,45,48,49]

        selected_dir_list  = []

        for i in selected_folder_index : 
            selected_dir_list.append(dir_list[i])

        
        folder_new = r"B:\BAMline-CT\2021\2021_10\Pch_2109_raw_h5"

        for dir in selected_dir_list:

            path_old = os.path.join(folder_old , dir)
            path_new = os.path.join(folder_new , dir)
            filename = dir + ".h5"

            #convert 
            data_path = "/entry/data/data"


            file_dic = create_file_dic(path_old,".tif",4) 
            for index in range (1,len(file_dic)):
            #for index in range (1,100):
                print(index)
                #read data  

                projection = tifffile.imread(file_dic[index])

                
                write_to_hdf(projection,data_path,filename,path_new)



    if test== 5 : 

        #in this folder , we have tiff files 
        file_dic = create_file_dic(r"E:\sdayani\2110a_set39_Pch_2109_12_85PhC_Y8575_48000eV_0p72um___500ms",".tif",4) 
        #start from file 1 till end. and do the following : 
        #read tiff file  
        #create a new h5 file or continue writing in it 
        
        
        folder_path = "testH5//"
        hfilename= "set39.h5"
        data_path = "/entry/data/data"

        for index in range (1,len(file_dic)):
        #for index in range (1,100):
            print(index)
            #read data  

            projection = tifffile.imread(file_dic[index])

            
            write_to_hdf(projection,data_path,hfilename,folder_path)





    if test ==1 : 
        

        test_data_1d = np.zeros(shape=(1))
        test_data_3d = np.ones(shape=(1,10,10))

        write_to_hdf(test_data_1d,"1ddata","test5.h5","testH5//")


    elif test==4 : #convert all data measured for PCH14 : 

        dir_list  = os.listdir(r"A:\BAMline-CT\2021\2021_12\PCH_14")
        #exclude the first one , already converted : 
        dir_list  = dir_list[1:]

        
        data_groups_hf = [

            '/entry/instrument/NDAttributes/CT-Kamera-Z',
            '/entry/instrument/NDAttributes/CT-Table_Y',
            '/entry/instrument/NDAttributes/CT_MICOS_W',
            '/entry/instrument/NDAttributes/CT_MICOS_X',
            '/entry/instrument/NDAttributes/CT_Piezo_X45',
            '/entry/instrument/NDAttributes/CT_Piezo_Y45',
            '/entry/instrument/NDAttributes/DMM_Energy',
            '/entry/instrument/NDAttributes/DMM_Theta_1',
            '/entry/instrument/NDAttributes/DMM_X',
            '/entry/instrument/NDAttributes/EULER_PITCH',
            '/entry/instrument/NDAttributes/EULER_ROLL',
            '/entry/instrument/NDAttributes/EXP_Y',
            '/entry/instrument/NDAttributes/K6485-1',
            '/entry/instrument/NDAttributes/NDArrayEpicsTSSec',
            '/entry/instrument/NDAttributes/NDArrayEpicsTSnSec',
            '/entry/instrument/NDAttributes/NDArrayTimeStamp',
            '/entry/instrument/NDAttributes/NDArrayUniqueId',
            '/entry/instrument/NDAttributes/RingCurrent'
        ] 
        extract_dic={}
        extract_dic["1D_data_path"] = data_groups_hf
        extract_dic["Projectein_data_path"] = "/entry/data/data"
        folder_old = r"A:\BAMline-CT\2021\2021_12\PCH_14"
        folder_new = r"B:\BAMline-CT\2021\2021_12\PCH_14_converted_raw"

        for dir in dir_list:

            path_old = os.path.join(folder_old , dir)
            path_new = os.path.join(folder_new , dir)
            filename = dir + ".h5"


            convert_(path_old,extract_dic,path_new,filename)



    elif test==3:


        data_groups_hf = [

            '/entry/instrument/NDAttributes/CT-Kamera-Z',
            '/entry/instrument/NDAttributes/CT-Table_Y',
            '/entry/instrument/NDAttributes/CT_MICOS_W',
            '/entry/instrument/NDAttributes/CT_MICOS_X',
            '/entry/instrument/NDAttributes/CT_Piezo_X45',
            '/entry/instrument/NDAttributes/CT_Piezo_Y45',
            '/entry/instrument/NDAttributes/DMM_Energy',
            '/entry/instrument/NDAttributes/DMM_Theta_1',
            '/entry/instrument/NDAttributes/DMM_X',
            '/entry/instrument/NDAttributes/EULER_PITCH',
            '/entry/instrument/NDAttributes/EULER_ROLL',
            '/entry/instrument/NDAttributes/EXP_Y',
            '/entry/instrument/NDAttributes/K6485-1',
            '/entry/instrument/NDAttributes/NDArrayEpicsTSSec',
            '/entry/instrument/NDAttributes/NDArrayEpicsTSnSec',
            '/entry/instrument/NDAttributes/NDArrayTimeStamp',
            '/entry/instrument/NDAttributes/NDArrayUniqueId',
            '/entry/instrument/NDAttributes/RingCurrent'
        ] 
        extract_dic={}
        extract_dic["1D_data_path"] = data_groups_hf
        extract_dic["Projectein_data_path"] = "/entry/data/data"
        path_old = r"E:\sdayani\211208_2131_81_PCH_14_operando_Z20_Y8500_48000eV_0p72um_500ms"
        path_new = r"E:\sdayani\211208_2131_81_PCH_14_operando_Z20_Y8500_48000eV_0p72um_500ms_new"

        convert_(path_old,extract_dic,path_new,"211208_2131_81_PCH_14_operando_Z20_Y8500_48000eV_0p72um_500ms.h5")

    elif test== 2 :
        file_dic = create_file_dic(r"E:\sdayani\211208_2131_81_PCH_14_operando_Z20_Y8500_48000eV_0p72um_500ms") 
        #start from file 1 till end. and do the following : 
        #read the h5 file 
        #create a new h5 file or continue writing in it 
        angle_path = '/entry/instrument/NDAttributes/CT_MICOS_W'
        data_path = "/entry/data/data"
        folder_path = "testH5//"
        hfilename= "projectionTest4.h5"
        for index in range (1,len(file_dic)):
        #for index in range (1,100):
            print(index)
            #read data from the h5 file 
            f = h5py.File(file_dic[index], "r")
            w_position = f[angle_path]
            w_data = w_position[:]
            write_to_hdf(w_data,angle_path,hfilename,folder_path)
            projection_proxy = f[data_path]
            projection =projection_proxy[:]
            
            write_to_hdf(projection,data_path,hfilename,folder_path)

            f.close()
