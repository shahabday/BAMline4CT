'''
This module is written based on ASTRA and tomopy , to gather all reconstruction routines 


on the fly reconstruction 
    180 degrees or limited angle 
    360 degrees
one slice reconstruction 
total reconstruction 


this module gets paramteres such as :
    CT mode : 180 / 360 or more 
    COR 
    projections 
    dark field 
    volume proxy of the projections from hdf5 file



and returns : 
    once slice reconstruction 
    total reconstruction 

    in : 
    16 bit 
    32 float 

GPU acccelerated operations using Tensors will be implemented using pytorch or TensorFlow 


this code is under custruction. 
all ideas to be implemented later are marked with :
    #!@

'''

import logging
import numpy as np 
import tomopy
from projection_import import *
from scipy.ndimage import rotate
from scipy.ndimage import interpolation

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

class Reconstruction:


    def __init__(self, ProjectionFile, scan_type = 'on-the-fly'  ) :
        
        #initialize variables

        # projectionFile : is an object created from ProjectionFile class


        #initialize type of CT :
        #   hdf5 ?
        #   on the fly ?
        #   360 or limited angle ?
        
        #!@ assert if projectionFile is the correct object
        if ProjectionFile.type == "h5" :
            logging.info("projection file is HDF5 File object ")
            self.FileObject = ProjectionFile
            

        else :#!@ elif for other file types
            logging.info("reconstruction for non hdf5 is not implemented yet")
 
        self.isNormalized_one_slice = False  # to check if we have normalized one slice already

        self.scan_type = scan_type #on the fly or step scan 
        
        
        

    #On-the-fly essential calculation function :
    def change_scan_type(self): # copied from HM code dont know what to do with this yet this is refrence to our code as angle range 
        self.new = 1

        if self.comboBox_180_360.currentText() == '180 - axis centered':
            self.extend_FOV_fixed_ImageJ_Stream = 0.15
        else:
            self.extend_FOV_fixed_ImageJ_Stream = 1.15
        print('extend FOV',self.extend_FOV_fixed_ImageJ_Stream)

        self.check()

    #On-the-fly essential calculation function :
    def one_slice_normalization(self):
        #normalize projections to reconstruct only one slice 

        #must be called when self.number_of_FFs is filled : this gets filled when reconstruction for one slice is called



        FFs = self.FileObject.vol_proxy[0:self.number_of_FFs -1, self.slice_number, :]
        FFmean = np.mean(FFs, axis=0)

        #sinogram 
        Sino = self.FileObject.vol_proxy[self.number_of_FFs : -self.number_of_FFs, self.slice_number, :]

        #normalize
        self.Norm = np.divide(np.subtract(Sino, self.DarkFieldValue), np.subtract(FFmean, self.DarkFieldValue + self.backIlluminationValue))

        self.isNormalized_one_slice = True

    #On-the-fly essential calculation function :
    def calculate_rotation_speed ( self , angle_list ): 
         

        #uses following variables to calculate img rotation speed : 
        #
        # number of FFs
        # angle list 
        #
        #last zero projection is also calculated and kept in a property of class

        graph= np.array(angle_list[self.number_of_FFs:-self.number_of_FFs])

        #calculating rotation speed : 
        poly_coeff = np.polyfit(np.arange(len(graph[round((graph.shape[0] + 1) /4) : round((graph.shape[0] + 1) * 3/4) ])), graph[round((graph.shape[0] + 1) /4) : round((graph.shape[0] + 1) * 3/4) ], 1, rcond=None, full=False, w=None, cov=False)
        print('Polynom coefficients {}    Detected angular step per image: {} '.format(poly_coeff,poly_coeff[0]))
        self.speed_W = poly_coeff[0] #rotation-speed[°/img]

        
        #find rotation start
        i = 0
        while i < graph.shape[0]:
            if round(graph[i]) == 0:  # notice the last projection at below 0.5°
                last_zero_proj = i + 3  # assumes 3 images for speeding up the motor
            i = i + 1
        
        self.last_zero_proj = last_zero_proj

        return self.speed_W


    def on_the_fly_one_slice (self, reco_settings):

        #This function is developed for the following projection file :
        #The projection file is stored in an HDF5 format containing : 
        #   all projection files
        #   FFs in the beginning of the projection files
        #   angle list stored in metadata 

        #we have ProjectionFiles stored in FileObject

        #reco_setting :  is a dictionary with all variables needed for reconstruction and reading the data 


         

        angle_list_dir = reco_settings['angle_list_dir'] # path in HDF5 file where angle list are stored
        
        if self.isNormalized_one_slice == True : # if we already did a FF normalization, check wheather any of these parameters are changed :

            if ((self.number_of_FFs != reco_settings["number_of_FFs"]) or \
                (self.slice_number != reco_settings["slice_number"]) or \
                (self.DarkFieldValue != reco_settings["DarkFieldValue"])\
                 or (self.backIlluminationValue != reco_settings["backIlluminationValue"])) :

                self.is_normalized = False # then we need to normalize the slice again



        self.number_of_FFs = reco_settings["number_of_FFs"] # this is needed in other functions 
        self.slice_number = reco_settings["slice_number"]  # this is needed in other functions 
        self.DarkFieldValue = reco_settings["DarkFieldValue"]# this is needed in other functions 
        self.backIlluminationValue = reco_settings["backIlluminationValue"]# this is needed in other functions 
        
        COR = reco_settings["COR"]
        Offset_Angle = reco_settings["Offset_Angle"]
        angle_range  = reco_settings["angle_range"]
        extend_FOV_fixed_ImageJ_Stream = reco_settings["extend_FOV_fixed_ImageJ_Stream"]
        reco_algorithm= reco_settings["reco_algorithm"]
        filter_name = reco_settings["filter_name"]
        pixel_size= reco_settings["pixel_size"]


        

        angle_list = self.FileObject.metadata_dic[angle_list_dir]
        graph= np.array(angle_list[self.number_of_FFs:-self.number_of_FFs])

        
        #find rotation start
        i = 0
        while i < graph.shape[0]:
            if round(graph[i]) == 0:  # notice the last projection at below 0.5°
                last_zero_proj = i + 3  # assumes 3 images for speeding up the motor
            i = i + 1

        
        #estimate COR
        if COR == 0:
            COR = (round(self.FileObject.vol_proxy.shape[2] / 2))


        #get Normalized Sinogram from one_slice_normalization(self)
        #check if already normallized or need to be normallized again as it takes time
        # this needs to be called if any of these variables change : 
        # self.slice_number 
        # self.DarkFieldValue  
        # self.backIlluminationValue
        # this is implemented in the beginning of the function. using isNormalized_one_slice

        if self.isNormalized_one_slice == False : 
            self.one_slice_normalization()
            #the normalized sinogram is stored in self.Norm


    
        #ring artifact handling 
        #!@ will be implemented later
        #   a function for ring artifact should be developed. and upon request , called here

        #calculating rotation speed : 
        poly_coeff = np.polyfit(np.arange(len(graph[round((graph.shape[0] + 1) /4) : round((graph.shape[0] + 1) * 3/4) ])), graph[round((graph.shape[0] + 1) /4) : round((graph.shape[0] + 1) * 3/4) ], 1, rcond=None, full=False, w=None, cov=False)
        print('Polynom coefficients {} \t Detected angular step per image: {} '.format(poly_coeff,poly_coeff[0]))
        self.speed_W = poly_coeff[0] #rotation-speed[°/img]


        #reconstruction :
        number_of_projections = self.Norm.shape[0]

        
        #check if the scan was 180° or 360°
        if number_of_projections * self.speed_W >= 270:
            number_of_used_projections = round(360 / self.speed_W)
        else:
            #print('smaller than 3/2 Pi')
            number_of_used_projections = round(180 / self.speed_W)

        
        # create list with all projection angles  based on radian 
        new_list = (np.arange(number_of_used_projections) * self.speed_W + Offset_Angle) * np.pi / 180

        # create list with x-positions of projections
        full_size = self.Norm.shape[1]

        if angle_range == '360 - axis right':
            center_list = [COR + round((extend_FOV_fixed_ImageJ_Stream -1) * full_size)] * (number_of_used_projections)
            #center_list = [self.COR.value() +  self.full_size] * (self.number_of_used_projections)
        else:
            center_list = [COR + round(extend_FOV_fixed_ImageJ_Stream * full_size)] * (number_of_used_projections)

        
        # create one sinogram in the form [z, y, x]
        transposed_sinos = np.zeros((min(number_of_used_projections, self.Norm.shape[0]), 1, full_size), dtype=float)
        transposed_sinos[:,0,:] = self.Norm[last_zero_proj : min(last_zero_proj + number_of_used_projections, self.Norm.shape[0]),:]

        #extend data with calculated parameter, compute logarithm, remove NaN-values
        extended_sinos = tomopy.misc.morph.pad(transposed_sinos, axis=2, npad=round(extend_FOV_fixed_ImageJ_Stream * full_size), mode='edge')

        # for 360° scans crop the padded area opposite of the axis

        if angle_range == '360 - axis right':
            
            extended_sinos = extended_sinos[:,:, full_size : ]

        elif angle_range == '360 - axis left':
            
            extended_sinos = extended_sinos[:,:, : - full_size]


        #calculate -log
        extended_sinos = tomopy.minus_log(extended_sinos)

        #clean data
        extended_sinos = np.nan_to_num(extended_sinos, copy=True, nan=1.0, posinf=1.0, neginf=1.0)


        
        #!@ implement later : apply phase retrieval if desired 
        #   a function for ring artifact should be developed. and upon request , called here
        #   or this should be a separate function that takes extended sinos from here ? 



        #reconstruct one slice
        if reco_algorithm == 'FBP_CUDA':
            options = {'proj_type': 'cuda', 'method': 'FBP_CUDA'}
            slices = tomopy.recon(extended_sinos, new_list, center=center_list, algorithm=tomopy.astra, options=options)
        else:
            slices = tomopy.recon(extended_sinos, new_list, center=center_list, algorithm=reco_algorithm,
                                    filter_name=filter_name)

        # scale with pixel size to attenuation coefficients
        slices = slices * (10000/pixel_size)



        # trim reconstructed slice
        if angle_range == '180 - axis centered':
            slices = slices[:, round(extend_FOV_fixed_ImageJ_Stream * full_size / 2): -round(extend_FOV_fixed_ImageJ_Stream * full_size / 2),round(extend_FOV_fixed_ImageJ_Stream * full_size / 2): -round(extend_FOV_fixed_ImageJ_Stream * full_size / 2)]
        else:
            slices = slices[:, round((extend_FOV_fixed_ImageJ_Stream -1) * full_size): -round((extend_FOV_fixed_ImageJ_Stream -1) * full_size),round((extend_FOV_fixed_ImageJ_Stream -1) * full_size): -round((extend_FOV_fixed_ImageJ_Stream -1) * full_size)]

        slices = tomopy.circ_mask(slices, axis=0, ratio=1.0)
        original_reconstruction = slices[0, :, :]


        #At this point we need to return the reconstructed slice. the rest should be done in GUI 
        #also write this in reconstruction object. 

        # set image dimensions only for the first time or when scan-type was changed

        # write results to PV . image viewer 

        self.one_slice_reconstructed = original_reconstruction

        return self.one_slice_reconstructed


    #On-the-fly essential calculation function :
    def normalization_cpu (self,FFs_vol,Sino_vol ):
        # input : 
        # FFs volume
        # Sinogram Volume

        FFmean_vol = np.mean(FFs_vol, axis=0)

        Norm_vol = np.divide(Sino_vol - self.DarkFieldValue, FFmean_vol - self.DarkFieldValue - self.backIlluminationValue)
        return Norm_vol


    def prepare_reco_metadata (self , *metadata):
        """
        preparing a table of metadata for printing, saving in hdf5 or csv 

        input : dictionary *metadata : as many as possible 
        
        """
        #some metadata should be written regardless of type and settings of reco algorithm 

        #meta_out = []
        # this is not implemented yet
        pass


        

    def on_the_fly_volume_reco (self, reco_settings, save_settings, slices_to_reco= 'all'):
        """
        in this function the whole volume or part of the volume storted in FileObject will be reconstructed

        needed inputs are : 

        slices_to_reco : if not changed, the whole volume will be reconstructed 
                        : if a part of volume is wished to be reconstructed :
                        its a tuple (first_slice, last_slice)
        reco_settings :
        reco_settings['angle_list_dir'] # path in HDF5 file where angle list are stored
        reco_settings["number_of_FFs"] # this is needed in other functions 
        reco_settings["DarkFieldValue"]# this is needed in other functions 
        reco_settings["backIlluminationValue"]# this is needed in other functions 
        reco_settings["Offset_Angle"]
        reco_settings["COR"]
        reco_settings["reco_algorithm"]
        reco_settings["filter_name"]
        reco_settings["n_cores"]
        reco_settings["block_size"]
        reco_settings["pixel_size"]


        save_settings  : 
        save_settings["dtype"]  uint16 or float32
        save_settings["fileType"] tif or h5
        save_settings["chunking"] None, int or  (1,w,h)
        save_settings["save_folder"] 

        
        """
        len_all_slices =self.FileObject.vol_proxy.shape[1] # height of projection equals to depth of CT

        def tuple_int(v):
            return isinstance(v, tuple) and list(map(type, v)) == [int, int]

        def reco_all ():
            return (0,len_all_slices) # reconstruct all

        def slice_in_range (v):
            if (v[0] <0 or v[0]>v[1] or v[0] > len_all_slices) : 
                return False
            if (v[1]<0 or v[1]<v[0] or v[1]> len_all_slices):
                return False 
            else : 
                return True 

        if slices_to_reco != 'all' : # a range of slices is selected 
            if tuple_int(slices_to_reco) and slice_in_range(slices_to_reco): # check if it is tuple with two int values are in range
                logging.info("Reconstruct a part of volume is selected {}".format (slices_to_reco))
            else :
                slices_to_reco = reco_all() # if not, auto select all vol to reconstruct
                logging.info("Reconstruct whole volume is autoselected ")
        elif slices_to_reco == 'all':
            slices_to_reco = reco_all()
            logging.info("Reconstruct whole volume is selected ")

                


        
        if save_settings["dtype"] == "uint16":
            #check for low and high value cropping
            if not "low_value" in save_settings.keys():
                logging.warning ("int 16 conversion needs low value")
                save_settings["low_value"] = 0
            if not "high_value" in save_settings.keys():
                logging.warning ("int 16 conversion needs high value")
                save_settings["high_value"] = 65535
        


        angle_list_dir = reco_settings['angle_list_dir'] # path in HDF5 file where angle list are stored
        self.number_of_FFs = reco_settings["number_of_FFs"] # this is needed in other functions 
        
        self.DarkFieldValue = reco_settings["DarkFieldValue"]# this is needed in other functions 
        self.backIlluminationValue = reco_settings["backIlluminationValue"]# this is needed in other functions 
        
        COR = reco_settings["COR"]
        Offset_Angle = reco_settings["Offset_Angle"]

        reco_algorithm= reco_settings["reco_algorithm"]
        filter_name = reco_settings["filter_name"]
        n_cores = reco_settings["n_cores"]
        self.block_size= reco_settings["block_size"]
        pixel_size= reco_settings["pixel_size"]

        #extend FOV
        #determine how far to extend field of view (FOV), 0.0 no extension, 0.5 half extension, 1.0 full extension to both sides (for off center 360 degree scans!!!)
        # substitute Norm.shape[1] with something else. that can reflect the width of sinogram 

        image_width = self.FileObject.vol_proxy.shape[2]
        self.extend_FOV = (2 * (abs(COR - image_width/2))/ (image_width)) + 0.15

        #calculate speed W
        angle_list = self.FileObject.metadata_dic[angle_list_dir]
        self.calculate_rotation_speed(angle_list)
        
        #calculate number of projections 
        # using FFs we should calculate number of projectiosn 
        self.number_of_projections = self.FileObject.vol_proxy.shape[0] - 2*self.number_of_FFs

        #check if 180° or 360°-scan
        if self.number_of_projections * self.speed_W >= 270:
            self.number_of_used_projections = round(360 / self.speed_W)
        else:
            #('smaller than 3/2 Pi')
            self.number_of_used_projections = round(180 / self.speed_W)
        logging.info('number of used projections {}'.format( self.number_of_used_projections))

        #create list with projection angles
        new_list = (np.arange(self.number_of_used_projections) * self.speed_W + Offset_Angle) * np.pi / 180
        # create list with COR-positions
        center_list = [COR + round(self.extend_FOV * image_width)] * (self.number_of_used_projections)
        #save reco parameters in metadata dictionary 
        
        #metadata  = {}
        #this is not implemented yet
        #divide volume into blocks and reconstruct them 

        #reconstruction : 

        #select block-wise : 
        writer = FileWrite(save_settings["save_folder"])
        counter = 0

        number_of_selected_slices = slices_to_reco[1] - slices_to_reco[0]

        
        while ( counter <np.ceil(number_of_selected_slices/self.block_size )):

            logging.info('Reconstructing block {} of {}'.format(counter + 1, np.ceil(number_of_selected_slices/ self.block_size)))
            
            #normalize using FFs
            #make Sinogram
            logging.info('Flat Field Normalization of block: {} '.format( counter +1))
            print ("number_of_selected_slices :" ,number_of_selected_slices )
            print ("slices_to_reco :" ,slices_to_reco )
            print ("slices_to_reco[0] + (self.block_size* (counter +1)) :" ,slices_to_reco[0] + (self.block_size* (counter +1))) 

            # end of fancy slicing is : first_slice + (blocksize* (counter +1))
            FFs_vol = self.FileObject.vol_proxy[0:self.number_of_FFs - 1, slices_to_reco[0] + (self.block_size* (counter)): slices_to_reco[0] + (self.block_size* (counter +1)), :]
            Sino_vol = self.FileObject.vol_proxy[self.number_of_FFs: -self.number_of_FFs, slices_to_reco[0] + (self.block_size* (counter )): slices_to_reco[0] + (self.block_size* (counter +1)), :]
            self.Norm_vol = self.normalization_cpu(FFs_vol,Sino_vol)
            logging.info('Normalized volume created ')
            
            #


            #!@ ring artifact handling will be implemented later 

            #extend data, take logarithm, remove NaN-values
            extended_sinos = self.Norm_vol[self.last_zero_proj : min(self.last_zero_proj + self.number_of_used_projections, self.Norm_vol.shape[0]), :, :]
            extended_sinos = tomopy.misc.morph.pad(extended_sinos, axis=2, npad=round(self.extend_FOV * image_width), mode='edge')
            extended_sinos = tomopy.minus_log(extended_sinos)
            extended_sinos = np.nan_to_num(extended_sinos, copy=True, nan=1.0, posinf=1.0, neginf=1.0)

            #!@ phase retrival 

            #reconstruct using selected algorithm 
            #add multiple core reconstruction 
            #reconstruct 
            if reco_algorithm == 'FBP_CUDA':
                options = {'proj_type': 'cuda', 'method': 'FBP_CUDA'}
                slices = tomopy.recon(extended_sinos, new_list, center=center_list, algorithm=tomopy.astra,
                                      options=options)
            else:
                slices = tomopy.recon(extended_sinos, new_list, center=center_list,
                                      algorithm=reco_algorithm,
                                      filter_name=filter_name,
                                      ncore=n_cores)

            # scale with pixel size to attenuation coefficients
            slices = slices * (10000 / pixel_size)

            #crop reconstructed data
            slices = slices[:, round(self.extend_FOV * image_width /2): -round(self.extend_FOV * image_width /2), round(self.extend_FOV * image_width /2): -round(self.extend_FOV * image_width /2)]
            slices = tomopy.circ_mask(slices, axis=0, ratio=1.0)

            #!@ convert it to 16 or 32 bit 
            if save_settings["dtype"] == "uint16" : 
                #convert to 16 bits
                #16-bit integer conversion
                ima3 = 65535 * (slices - save_settings["low_value"]) / (save_settings["high_value"] - save_settings["low_value"])
                ima3 = np.clip(ima3, 1, 65534)
                slices = ima3.astype(np.uint16)

            

            if (save_settings["fileType"] == "tif" or save_settings["fileType"] == "tiff"):
                #save in tiffstacks 
                # write the reconstructed block to disk as TIF-file
                #def saveTiff_volume (self, vol , fname , ind_offset = 0 , type= 'float32'):

                writer.saveTiff_volume(slices , self.FileObject.filename , ind_offset = counter * self.block_size,
                                 type = save_settings["dtype"])


            elif (save_settings["fileType"] == "h5") : 
                #save in hdf File
                #write_hdf_volume (self, vol , fname , chunking = None , dataset_name = "Volume"):
                writer.write_hdf_volume(slices, self.FileObject.filename , 
                                    chunking = save_settings["chunking"], dataset_name = "Volume")


            counter += 1

        if (save_settings["fileType"] == "tif" or save_settings["fileType"] == "tiff"):
                #save metadata in csv file 
                pass

        elif (save_settings["fileType"] == "h5") : 
            #save meta data in hdf File
            #writer.write_hdf_metadata(metadata , self.FileObject.filename , "/reco_settings/")
            pass

     

    def one_slice_reco (self):



        pass
        #if imaging mode 
        #if tomo mode == on the Fly

    def reconstruct_volume (self):
        pass

    def save_reconstruction (self ):
        pass

        #use another module for saveing 
        
        
if __name__ == "__main__": 
    from reconstruct import * 

    from projection_import import * 

    import matplotlib.pylab as plt


    FileObject = ProjectionFile("A:\\BAMline-CT\\2022\\2022_03\\Pch_21_09_10\\220317_1754_95_Pch_21_09_10_____Z40_Y8300_42000eV_10x_250ms\\220317_1754_95_00001.h5")
    _,metadata = FileObject.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])


    reco_setting ={} 
    reco_setting['angle_list_dir'] = '/entry/instrument/NDAttributes/CT_MICOS_W'
    reco_setting["number_of_FFs"] = 20 
    reco_setting["slice_number"]  = 10
    reco_setting["DarkFieldValue"] = 200
    reco_setting["backIlluminationValue"] = 0
    reco_setting["COR"] = 1213
    reco_setting["Offset_Angle"] = 0
    reco_setting["angle_range"] = '180 - axis centered'
    reco_setting["extend_FOV_fixed_ImageJ_Stream"] = 0.25
    reco_setting["reco_algorithm"] = 'gridrec'
    reco_setting["filter_name"] = "shepp"
    reco_setting["pixel_size"] = 0.72

    recoObject=Reconstruction(FileObject)
    #slice = recoObject.on_the_fly_one_slice(reco_setting)
    #writer = FileWrite("D:\\shahab\\HDF\\Writer\\3\\oneSlice")
    #writer.saveTiff(slice, "one-slice-slice_10")
    

    reco_settings={}

    reco_settings['angle_list_dir']='/entry/instrument/NDAttributes/CT_MICOS_W'# path in HDF5 file where angle list are stored
    reco_settings["number_of_FFs"] = 20 # this is needed in other functions 
    reco_settings["DarkFieldValue"] = 200# this is needed in other functions 
    reco_settings["backIlluminationValue"]= 0# this is needed in other functions 
    reco_settings["COR"] = 1213
    reco_settings["Offset_Angle"] = 0
    reco_settings["reco_algorithm"] = "gridrec"
    reco_settings["filter_name"] = "shepp"
    reco_settings["n_cores"] = 8
    reco_settings["block_size"] = 30
    reco_settings["pixel_size"] = 0.72


    #save_settings  : 
    save_settings = {}
    save_settings["dtype"] = "float32"# or float32
    save_settings["fileType"] = "tif"
    save_settings["chunking"] = None
    save_settings["save_folder"] = "D:\\shahab\\HDF\\Writer\\4"

    recoObject.on_the_fly_volume_reco(reco_settings,save_settings) #this saves automatically the volume 


