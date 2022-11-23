


'''
This module is written to set up the EPICS pluging for ImageJ
This helps cleaning up our codes and also to establish more than one viewer in a program
default set up values will be written in a dictionary in the class so that we can call them easily
but the code is general enough to edit settings on the go 

#Install ImageJ-PlugIn: EPICS AreaDetector NTNDA-Viewer, look for the channel specified here under channel_name, consider multiple users on servers!!!
channel_name = 'BAMline:CTReco'

pip install pvapy


'''


import pvaccess as pva      


class ImageJViewer:


    def __init__(self,channel_name, pva_image_dict = "default"):


        #default setting for pva image 
        self.pva_image_default_dict = {'value': ({'booleanValue': [pva.pvaccess.ScalarType.BOOLEAN], 'byteValue':
            [pva.pvaccess.ScalarType.BYTE], 'shortValue': [pva.pvaccess.ScalarType.SHORT], 'intValue':
            [pva.pvaccess.ScalarType.INT], 'longValue': [pva.pvaccess.ScalarType.LONG], 'ubyteValue':
            [pva.pvaccess.ScalarType.UBYTE], 'ushortValue': [pva.pvaccess.ScalarType.USHORT], 'uintValue':
            [pva.pvaccess.ScalarType.UINT], 'ulongValue': [pva.pvaccess.ScalarType.ULONG], 'floatValue':
            [pva.pvaccess.ScalarType.FLOAT], 'doubleValue': [pva.pvaccess.ScalarType.DOUBLE]},), 'codec':
            {'name': pva.pvaccess.ScalarType.STRING, 'parameters': ()}, 'compressedSize':
            pva.pvaccess.ScalarType.LONG, 'uncompressedSize': pva.pvaccess.ScalarType.LONG, 'dimension':
            [{'size': pva.pvaccess.ScalarType.INT, 'offset': pva.pvaccess.ScalarType.INT, 'fullSize':
                pva.pvaccess.ScalarType.INT, 'binning': pva.pvaccess.ScalarType.INT, 'reverse':
                pva.pvaccess.ScalarType.BOOLEAN}], 'uniqueId': pva.pvaccess.ScalarType.INT, 'dataTimeStamp':
            {'secondsPastEpoch': pva.pvaccess.ScalarType.LONG, 'nanoseconds': pva.pvaccess.ScalarType.INT,
             'userTag': pva.pvaccess.ScalarType.INT}, 'attribute':
            [{'name': pva.pvaccess.ScalarType.STRING, 'value': (), 'descriptor': pva.pvaccess.ScalarType.STRING,
              'sourceType': pva.pvaccess.ScalarType.INT, 'source': pva.pvaccess.ScalarType.STRING}], 'descriptor':
            pva.pvaccess.ScalarType.STRING, 'alarm': {'severity': pva.pvaccess.ScalarType.INT, 'status':
            pva.pvaccess.ScalarType.INT, 'message': pva.pvaccess.ScalarType.STRING}, 'timeStamp':
            {'secondsPastEpoch': pva.pvaccess.ScalarType.LONG, 'nanoseconds': pva.pvaccess.ScalarType.INT, 'userTag':
                pva.pvaccess.ScalarType.INT}, 'display': {'limitLow': pva.pvaccess.ScalarType.DOUBLE, 'limitHigh':
            pva.pvaccess.ScalarType.DOUBLE, 'description': pva.pvaccess.ScalarType.STRING, 'format':
            pva.pvaccess.ScalarType.STRING, 'units': pva.pvaccess.ScalarType.STRING}}


        self.image_dimensions_sent = False 
        self.current_image_dimensions = None
          
        if pva_image_dict == "default" : 

            pva_image_dict = self.pva_image_default_dict


        self.pv_rec = pva.PvObject(pva_image_dict)
        self.pvaServer = pva.PvaServer(channel_name, self.pv_rec)
        self.pvaServer.start()


        
    def send_image(self,image):
        #set image dimensions for the first time we initiate this :
        if self.current_image_dimensions != image.shape:
            self.image_dimensions_sent = False

        if self.image_dimensions_sent == False : 
            self.pv_rec['dimension'] = [
                {'size': image.shape[0], 'fullSize': image.shape[0], 'binning': 1},
                {'size': image.shape[0], 'fullSize': image.shape[0], 'binning': 1}]
            self.current_image_dimensions = image.shape
            self.image_dimensions_sent = True
        
        #send data to ImageJ viewer
        self.pv_rec['value'] = ({'floatValue': image.flatten()},)

    def send_second_time (self, image):
        self.pv_rec['value'] = ({'floatValue': image.flatten()},)
            


 
if __name__ == '__main__':
    import numpy as np 
    from PIL import Image
    
    test = ImageJViewer("CT4D")

    list_of_path = [r"B:\BAMline-CT\2022\2022_10\663_221020_1846_00001\663_221020_1846_00001_0075.tif",
                    r"B:\BAMline-CT\2022\2022_10\663_221020_1846_00001\663_221020_1846_00001_1175.tif",
                    r"B:\BAMline-CT\2022\2022_10\663_221020_1846_00001\663_221020_1846_00001_1176.tif"]

    for i_path in list_of_path:
        image = Image.open(i_path)


        image = np.array(image)
        image = np.float32(image)

    
        test.send_image(image)

    