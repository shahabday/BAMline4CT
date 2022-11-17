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

from timeit import default_timer as timer #just for development purposes 
from projection_import import *
from scipy.ndimage.filters import gaussian_filter, median_filter

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
try:
    import torch
    logging.info("PyTorch Imported succesfully")
    torch_exists = True
except ModuleNotFoundError as err:
    torch_exists = False
    # Error handling
    print(err)


#pretty printing 
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Reconstruction:


    def __init__(self, ProjectionFile, gpu = False  ) :

        self.gpu_is_available = False
        if torch_exists == True :
            if gpu == True : 
                if torch.cuda.is_available() : 
                    torch.device("cuda")
                    self.gpu_is_available = True
                    self.gpu_name = torch.cuda.get_device_name(0)
                    logging.info("GPU : {} ".format(self.gpu_name))
                else: 
                    logging.info(" cannot find cuda ... ") 
        else:
            logging.info("Torch is not properly imported ... check installation")
        
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

        #testing purpose 
        #timing processing duration 
        
        self.copy_time  =[] 
        self.p_time = []

        
        
        

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


    def ring_artifact (self, Norm_vol , radius ):
        """
        ring artifact handeling : 
        developed originally by Henning Markoetter. 
        re-written for CPU and GPU by shahabeddin dayani

        implementation using GPU :
        the tensor stored in GPU memory having normallized projections, 
        should be fed to this function to save copying time from memory to GPU 
        
        """

        #2D projections sum =mean(normalized porjections )
        #assert proper dimensions 
        # filter the 2D projection sum using median filter 
        # correction map vol = projection sum / projection sum filtered
        # correction map vol = clip 0.9 and 1.1  limit values between 0.9 and 1.1

        #update normalized volume :
        # divide (normalized vol , correction map volume)

        if Norm_vol.ndim == 2 : # one slice :
            #implementation for slice reconstruction :
            logging.info("ring handeling for one slice started ") 
            proj_sum = np.mean(Norm_vol , axis=0)
            proj_sum=proj_sum.reshape(1, proj_sum.shape[0])
            proj_sum_filtered = median_filter(proj_sum , size = (1,radius), mode="nearest" )
            correction_map = np.divide(proj_sum , proj_sum_filtered)
            correction_map = np.clip(correction_map , 0.9,1.1)

            ring_filtered_norm = Norm_vol / correction_map
            logging.info("ring handeling finished ")

        elif Norm_vol.ndim == 3 : # volume
            logging.info("ring handeling for volume portion started ") 
            proj_sum = np.mean(Norm_vol , axis=0)
            proj_sum_filtered = median_filter(proj_sum,size= radius , mode="nearest")
            correction_map_vol = np.divide(proj_sum, proj_sum_filtered)
            correction_map_vol = np.clip(correction_map_vol,0.7,1.3) 
            ring_filtered_norm = Norm_vol/correction_map_vol
            logging.info("ring handeling finished ")

        return ring_filtered_norm
        
     

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
                 or (self.backIlluminationValue != reco_settings["backIlluminationValue"]) or 
                 self.ring_radius!= reco_settings["ring_radius"]) :
                    

                    self.isNormalized_one_slice = False # then we need to normalize the slice again



        self.number_of_FFs = reco_settings["number_of_FFs"] # this is needed in other functions 
        self.slice_number = reco_settings["slice_number"]  # this is needed in other functions 
        self.DarkFieldValue = reco_settings["DarkFieldValue"]# this is needed in other functions 
        self.backIlluminationValue = reco_settings["backIlluminationValue"]# this is needed in other functions 
        
        COR = reco_settings["COR"]
        Offset_Angle = reco_settings["offset_Angle"]
        angle_range  = reco_settings["angle_range"]
        extend_FOV_fixed_ImageJ_Stream = reco_settings["extend_FOV_fixed_ImageJ_Stream"]
        reco_algorithm= reco_settings["reco_algorithm"]
        filter_name = reco_settings["filter_name"]
        pixel_size= reco_settings["pixel_size"]
        self.ring_radius = reco_settings["ring_radius"]



        

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
            
            print("doing the normalization for : slice : {}".format(reco_settings["slice_number"]))
            
            self.one_slice_normalization()
            #the normalized sinogram is stored in self.Norm
            #ring artifact handling 
            #we dont need normalization for ring radius . this should be separated D
            if self.ring_radius != 0 :
                self.Norm=self.ring_artifact(self.Norm,self.ring_radius)
            

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

    def normalization_gpu( self, FFs_vol,Sino_vol):
        """
        normalization using gpu 

        """
        torch.cuda.empty_cache() 
        #pytorch accepts following dtypes : loat64, float32, float16, complex64, complex128, int64, int32, int16, int8, uint8, and bool
        start = timer()
        FFs_vol = torch.from_numpy(FFs_vol.astype(np.float32)).cuda() #converting to tensor must be int32
        Sino_vol = torch.from_numpy(Sino_vol.astype(np.float32)).cuda()
        end = timer()
        print('copy to GPU : ')
        print(end - start)
        
        self.copy_time.append(end - start)
        #self.copy_time = end - start


        # using mean function is only possible using floating dtype 
        #this has a bug . probably a lot of negative values exist due to float and also 
        # a lot of division by zeros 
        start = timer()
        FFmean_vol = torch.mean(FFs_vol, dim=0) # 
        Norm_vol = torch.divide(Sino_vol - self.DarkFieldValue, FFmean_vol - self.DarkFieldValue - self.backIlluminationValue)
        Norm_vol = Norm_vol.cpu().detach().numpy().astype(np.float32)
        end = timer()
        print('elapsed time on GPU : ')
        print(end - start)
        self.p_time.append(end - start)
        #self.p_time = end - start
        

        return Norm_vol

        

    #On-the-fly essential calculation function :
    def normalization_cpu (self,FFs_vol,Sino_vol ):
        # input : 
        # FFs volume
        # Sinogram Volume
        start= timer()
        FFmean_vol = np.mean(FFs_vol, axis=0)
        
        
        Norm_vol = np.divide(Sino_vol - self.DarkFieldValue, FFmean_vol - self.DarkFieldValue - self.backIlluminationValue)

        end = timer()
        print('elapsed time on CPU : ')
        print(end - start)
        self.p_time.append(end - start)
        #self.p_time = end - start


        return Norm_vol


    def prepare_reco_metadata (self , *metadatas):
        """
        preparing a table of metadata for printing, saving in hdf5 or csv 

        input : dictionary *metadata : as many as possible 

        Note : writing metadata in hdf5 file : 
        no value should be None
        
        """
        #some metadata should be written regardless of type and settings of reco algorithm 

        #meta_out = []
        # this is not implemented yet
        meta_out = {}
        for metadata in metadatas : 
            meta_out.update(metadata)

        #check for forbiden values : 
        #no None value is allowed for hdf5 

        for key, value in meta_out.items():
            if value == None :
                meta_out[key] = 0
            
        return meta_out



        

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
        reco_settings["offset_Angle"]
        reco_settings["COR"]
        reco_settings["reco_algorithm"]
        reco_settings["filter_name"]
        reco_settings["n_cores"]
        reco_settings["block_size"]
        reco_settings["pixel_size"]
        reco_settings["GPU"] = True, False


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
        Offset_Angle = reco_settings["offset_Angle"]

        reco_algorithm= reco_settings["reco_algorithm"]
        filter_name = reco_settings["filter_name"]
        n_cores = reco_settings["n_cores"]
        self.block_size= reco_settings["block_size"]
        pixel_size= reco_settings["pixel_size"]
        self.ring_radius = reco_settings["ring_radius"]


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
            #print ("slices_to_reco :" ,slices_to_reco )
            #print ("slices_to_reco[0] + (self.block_size* (counter +1)) :" ,slices_to_reco[0] + (self.block_size* (counter +1))) 

            # end of fancy slicing is : first_slice + (blocksize* (counter +1))
            FFs_vol = self.FileObject.vol_proxy[0:self.number_of_FFs - 1, slices_to_reco[0] + (self.block_size* (counter)): slices_to_reco[0] + (self.block_size* (counter +1)), :]
            Sino_vol = self.FileObject.vol_proxy[self.number_of_FFs: -self.number_of_FFs, slices_to_reco[0] + (self.block_size* (counter )): slices_to_reco[0] + (self.block_size* (counter +1)), :]
            if self.gpu_is_available == True and reco_settings["GPU"] == True : 
                self.Norm_vol = self.normalization_gpu(FFs_vol,Sino_vol)
            else: 
                self.Norm_vol = self.normalization_cpu(FFs_vol,Sino_vol)
            logging.info('Normalized volume created ')
            print(bcolors.WARNING +'copy_time : {} '.format(self.copy_time) + bcolors.ENDC  )
            print ("proccess_tiem : " ,self.p_time )
            
            
            
            #


            #!@ ring artifact handling 

            self.Norm_vol=self.ring_artifact(self.Norm_vol,self.ring_radius)


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


            elif (save_settings["fileType"] == "h5" or save_settings["fileType"]== "hdf5") : 
                #save in hdf File
                #write_hdf_volume (self, vol , fname , chunking = None , dataset_name = "Volume"):
                writer.write_hdf_volume(slices, self.FileObject.filename , 
                                    chunking = save_settings["chunking"], dataset_name = "Volume")


            counter += 1

        if (save_settings["fileType"] == "tif" or save_settings["fileType"] == "tiff"):
                #save metadata in csv file 
                pass

        elif (save_settings["fileType"] == "h5" or save_settings["fileType"] == "hdf5") : 
            #save meta data in hdf File
            
            #writer.write_hdf_metadata(metadata , self.FileObject.filename , "/reco_settings/")
            meta = self.prepare_reco_metadata(reco_settings, save_settings)
            writer.write_hdf_metadata(meta , self.FileObject.filename )

     

    def one_slice_reco (self):



        pass
        #if imaging mode 
        #if tomo mode == on the Fly

    def reconstruct_volume (self):
        pass

    def save_reconstruction (self ):
        pass

        #use another module for saveing 
        
if __name__ == "__main__" : 
    #test Writer and metadata writer : 
    
    from projection_import import *
    import numpy as np 

    FileObject = ProjectionFile("A:\\BAMline-CT\\2022\\2022_03\\Pch_21_09_10\\220317_1754_95_Pch_21_09_10_____Z40_Y8300_42000eV_10x_250ms\\220317_1754_95_00001.h5")
    _,metadata = FileObject.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])

    recoObject = Reconstruction(FileObject)

    reco_setting ={} 
    reco_setting['angle_list_dir'] = '/entry/instrument/NDAttributes/CT_MICOS_W'
    reco_setting["number_of_FFs"] = 20 
    reco_setting["slice_number"]  = 10
    reco_setting["DarkFieldValue"] = 200
    reco_setting["backIlluminationValue"] = 0

    save_settings = {}
    save_settings["dtype"] = "float32"# or float32
    save_settings["fileType"] = "tif"
    save_settings["chunking"] = None



    meta = recoObject.prepare_reco_metadata(reco_setting, save_settings)

    writer = FileWrite("E:\\sdayani\\HDFmetadataTest")
    vol = np.zeros(shape=(10,10,10))
    writer.write_hdf_volume(vol,"test3.h5")
    writer.write_hdf_metadata(meta,"test3.h5")
    

if __name__ == "__ffmain__": 

    # test the whole module 

    from reconstruct import * 

    from projection_import import * 

    import matplotlib.pylab as plt

    import pandas as pd

    FileObject = ProjectionFile("A:\\BAMline-CT\\2022\\2022_03\\Pch_21_09_10\\220317_1754_95_Pch_21_09_10_____Z40_Y8300_42000eV_10x_250ms\\220317_1754_95_00001.h5")
    _,metadata = FileObject.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])


    reco_setting ={} 
    reco_setting['angle_list_dir'] = '/entry/instrument/NDAttributes/CT_MICOS_W'
    reco_setting["number_of_FFs"] = 20 
    reco_setting["slice_number"]  = 10
    reco_setting["DarkFieldValue"] = 200
    reco_setting["backIlluminationValue"] = 0
    reco_setting["COR"] = 1213
    reco_setting["offset_Angle"] = 0
    reco_setting["angle_range"] = '180 - axis centered'
    reco_setting["extend_FOV_fixed_ImageJ_Stream"] = 0.25
    reco_setting["reco_algorithm"] = 'gridrec'
    reco_setting["filter_name"] = "shepp"
    reco_setting["pixel_size"] = 0.72

    recoObject=Reconstruction(FileObject  , gpu=True)
    #slice = recoObject.on_the_fly_one_slice(reco_setting)
    #writer = FileWrite("D:\\shahab\\HDF\\Writer\\3\\oneSlice")
    #writer.saveTiff(slice, "one-slice-slice_10")
    

    reco_settings={}

    reco_settings['angle_list_dir']='/entry/instrument/NDAttributes/CT_MICOS_W'# path in HDF5 file where angle list are stored
    reco_settings["number_of_FFs"] = 20 # this is needed in other functions 
    reco_settings["DarkFieldValue"] = 200# this is needed in other functions 
    reco_settings["backIlluminationValue"]= 0# this is needed in other functions 
    reco_settings["COR"] = 1213
    reco_settings["offset_Angle"] = 0
    reco_settings["reco_algorithm"] = "gridrec"
    reco_settings["filter_name"] = "shepp"
    reco_settings["n_cores"] = 16
    reco_settings["block_size"] = 60
    reco_settings["pixel_size"] = 0.72
    reco_settings["GPU"] = True 


    #save_settings  : 
    save_settings = {}
    save_settings["dtype"] = "float32"# or float32
    save_settings["fileType"] = "tif"
    save_settings["chunking"] = None
    save_settings["save_folder"] = "D:\\shahab\\HDF\\Writer\\{}"

    key_list = ["GPU" ,"block_size" , "save_folder" ]
    param_list = [True, 10 , "Gpu_10"] 

    def modify_setting (value):
        key_list = ["GPU" ,"block_size" , "save_folder" ]
        for k,v in zip(key_list,value):
            if  k == "save_folder":
                save_settings[k]= "D:\\shahab\\HDF\\Writer\\{}".format(v)
            else: 
                reco_settings[k] = v
                print ("this is my settings ")
                print(k , v )




    param_list = [[True, 10 , "Gpu_10"] , [True , 20 , "GPU_20"] , [True, 30 , "Gpu_30"] , [True, 50 , "Gpu_50"] ,[True, 16 , "Gpu_16"] , [True , 32 , "GPU_32"] , [True, 48 , "Gpu_48"] , [True, 64 , "Gpu_64"] ,
    [False, 10 , "Cpu_10"] , [False , 20 , "CPU_20"] , [False, 30 , "Cpu_30"] , [False, 50 , "Cpu_50"],[False, 16 , "Cpu_16"] , [False , 32 , "CPU_32"] , [False, 48 , "Cpu_48"] , [False, 64 , "Cpu_64"] ]


    #param_list = [[True, 30 , "Gpu_10"] , [False , 30 , "GPU_20"] ]

    #test speed of GPU operation and CPU operation 
    o_p_time = []
    o_c_time = []
    total_time = [ ]
    print ('start the looooooooop')
    for params in param_list : 
        print('making the empty ')
       
        
        modify_setting(params)

        s = timer()
        recoObject.on_the_fly_volume_reco(reco_settings,save_settings, slices_to_reco=(1, 500)) #this saves automatically the volume 
        e = timer()
        total_time.append(e-s)
        print (params)
        print(bcolors.WARNING +'copy_time : {} '.format(recoObject.copy_time) + bcolors.ENDC  )
        print ("proccess_tiem : " ,recoObject.p_time )

        o_p_time.append(recoObject.p_time)
        o_c_time.append(recoObject.copy_time)
        recoObject.p_time = []
        recoObject.copy_time = []

    pd.DataFrame(param_list).to_excel("prarm.xlsx")
    pd.DataFrame(o_p_time).to_excel("p_time.xlsx")
    pd.DataFrame(o_c_time).to_excel("c_time.xlsx")
    pd.DataFrame(total_time).to_excel("total_time.xlsx")


    


