
from projection_import import * 


test = ProjectionFile("A:\\BAMline-CT\\2022\\2022_03\\Pch_21_09_10\\220317_1754_95_Pch_21_09_10_____Z40_Y8300_42000eV_10x_250ms\\220317_1754_95_00001.h5")
print (test.file_extension)
print(test.filename)
print(test.directory)
print(test.type)
metadata = test.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])
print (metadata)

#self.line_proxy = f['/entry/instrument/NDAttributes/CT_MICOS_W']


