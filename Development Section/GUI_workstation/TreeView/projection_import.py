

'''
This module is written to be able to load recorded projection data and metadata for a CT measurment

The data could be saved in hdf5 format , or stack of tiffs . 
also the hdf5 format could have various metadata written in different folders or attribute. 

the function trys to be as universial as possible . 

input of this function is a file path. 
output of this function is : 
    if the file given is an hdf file :
        data_proxy  : an h5py object connecting us to the data set 
        metadata    : such as rotation speed, number of projections , etc 
        filepath    : folder path, filename , 

    if it is a series of TIFF files : 
        data_       : as numpy array
        metadata    : ? we shall define a mechansim for metadata. they are highly individual
        filepath    : folder path, filename 


'''

import os
import h5py
import logging
import tifffile


logging.getLogger().setLevel(logging.INFO)
logging.info('Reconstruction object Imported')

"""
Logging levels 
CRITICAL
ERROR
WARNING
INFO
DEBUG
NOTSET
"""



class ProjectionFile:

    def fileType(self):

        if self.file_extension == '.tif' or self.file_extension == '.tiff':
            return 'tif'
        elif self.file_extension == '.h5':
            return 'h5'
        else:
            logging.info('File extension not implemented')
            return None


    
    def __init__(self, fullPath):

        self.fullPath = fullPath

        _, self.file_extension = os.path.splitext(self.fullPath)
        self.directory=os.path.dirname(self.fullPath)
        self.filename=os.path.splitext(os.path.basename(self.fullPath))[0]
        self.type = self.fileType()


    def openFile(self,**kwargs):

        if self.type == 'h5':
            
            return self.openH5File(**kwargs)

        elif self.type == 'tif':
            print('tiff stack loading not yet implemented')

        else:
            print ("this file type is not implemented yet")


    def openH5File(self,**kwargs):

        '''
        this function opens an hdf5 file
        implementation of the kwarg is flexible and therefore this could be extended to 
        include various versions of hdf5 file

        we need to know : 
        path to the volume
        path to the selected metadata
            this could be more than one. 
            this is a list of metadata
        
        '''

        volume_path = kwargs["volume"]
        metadata_paths = kwargs["metadata"]
        
        f = h5py.File(self.fullPath, 'r')
        self.vol_proxy = f[volume_path]
        print('volume opened successfully : data shape: ', self.vol_proxy.shape)

        self.metadata_dic = {}
        for metadata in metadata_paths :
            self.metadata_dic[metadata] = f[metadata]

        return self.vol_proxy, self.metadata_dic

        
class FileWrite:

   
    def createFolder(self, pathFolder):

        if not os.path.exists(pathFolder):
            os.makedirs(pathFolder)
            logging.info("folder {} was created".format(pathFolder))

   
    def __init__(self, folder):

        self.folder = folder

    def write_hdf_metadata(self,metadata, fname , metadata_path = "metadata"):
        
        '''
        this function opens an existing hdf5 file and wirtes metadata to it
       
        '''
        
        hdf5_fullpath = os.path.join(self.folder,fname)
        #check if file extension is correct : 
        _, self.file_extension = os.path.splitext(hdf5_fullpath)
        if self.file_extension != ".h5" : 
            print("the hdf5 file extension is not correct")
            logging.warning ("the hdf5 file extension is not correct")
            fname = fname + ".h5"

        if  os.path.exists(hdf5_fullpath) :
        
            with h5py.File(hdf5_fullpath , 'r+') as f : 
                f.create_dataset(metadata_path, data = metadata)
                logging.info("metadata written to {}".format(fname))
        else:
            #file should alredy exist 
            logging.warning("HDF5 file doesnt exist {} ".format(hdf5_fullpath))


    def write_hdf_volume (self, vol , fname , chunking = None , dataset_name = "Volume"):
        
        '''
        vol : volume 3D numpy array
        chunking : when True , a tuple with (1, x_chunking, y_chunking )
                    it is recomended not to chunk an image width or height more than 1/4
        chunking : when : "auto"
                    look at volumes dimensions, divide it by 4 , and render chunking 
        chunking : if int :  for ex.  2, 4, 8, etc 
                    divide width and height by the int and render chunking 

        
        '''

        hdf5_fullpath = os.path.join(self.folder,fname)
        #check if file extension is correct : 
        _, self.file_extension = os.path.splitext(hdf5_fullpath)
        if self.file_extension != ".h5" : 
            print (self.file_extension)
            print("the hdf5 file extension is not correct")
            logging.warning ("the hdf5 file extension is not correct")
            fname = fname + ".h5"
            hdf5_fullpath = os.path.join(self.folder,fname)




        #chunking 
        if chunking is None :
            chunking = True

        

        #create folder if does not exist 
        self.createFolder(self.folder)

        
        #check if hdf file already exists : 
        if not os.path.exists(hdf5_fullpath) :
            #create hdf file if does not exist
            with h5py.File(hdf5_fullpath , 'w') as f : 
                f.create_dataset(dataset_name, data = vol , chunks = chunking , maxshape=(None, vol.shape[1], vol.shape[2]))
        else:
        #if exists, fill in the volume 
            #open h5 file 
            f = h5py.File(hdf5_fullpath,"r+")
            vol_proxy = f[dataset_name]
            shape = vol_proxy.shape

            vol_proxy.resize((shape[0] + vol.shape[0]), axis=0)

            vol_proxy[shape[0] : shape[0] + vol.shape[0] ,:,:] = vol

            #close file
            f.close()

  

    def saveTiff(self, img, fname, ind=0, type = 'float32'):

        #create folder
        self.createFolder(self.folder)
        #create fname
        fname = fname + '_' + str(ind).zfill(4)+'.tif'
        fullPath = os.path.join(self.folder, fname)
        tifffile.imsave(fullPath, img.astype(type))
                
    def saveTiff_volume (self, vol , fname , ind_offset = 0 , type= 'float32'):
        '''
        vol : numpy array of 3D volume  (z,x,y)
        ind_offset : the next image index will be in_offset 
        '''

        depth =vol.shape[0]
        for slice_no in range(depth):
            slice=vol[slice_no,:,:]
            self.saveTiff(slice , fname , ind=ind_offset + slice_no  , type=type)

 
if __name__ == '__main__':
    
    

    test = ProjectionFile("A:\\BAMline-CT\\2022\\2022_03\\Pch_21_09_10\\220317_1754_95_Pch_21_09_10_____Z40_Y8300_42000eV_10x_250ms\\220317_1754_95_00001.h5")
    print (test.file_extension)
    print(test.filename)
    print(test.directory)
    print(test.type)
    metadata = test.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])
    print (metadata)

    #self.line_proxy = f['/entry/instrument/NDAttributes/CT_MICOS_W']

    #test saving hdf5 file 

    vol = test.vol_proxy [1:20,:,:]

    writer = FileWrite("D:\\shahab\\HDF\\Writer")
    writer.write_hdf_volume(vol, "firsttest5.h5")
    writer.write_hdf_volume(vol,"firsttest5.h5" )
    writer.write_hdf_metadata("metadata", "firsttest5.h5" , "/meta")
    writer.folder = "D:\\shahab\\HDF\\Writer\\tiff"
    writer.saveTiff_volume(vol, "projection" , ind_offset=5 , type = "uint16")
