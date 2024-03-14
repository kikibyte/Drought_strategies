# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:20:57 2024

@author: chenq4
"""


import numpy as np
import gdal
import gdalconst   
from itertools import accumulate

#function for calculating accumulation
def get_accum(yearablai):
    if np.all(np.isnan(yearablai)):
        ablai_accum=np.zeros((730))
        ablai_accum=ablai_accum*np.NaN
    else:
        yearablai[np.isnan(yearablai)]=0.0
        yearablai[np.where(yearablai>-1)]=0.0
        ablai_accum=list(accumulate(yearablai))
    return ablai_accum 

#function for reading and calculating in blocks
def wirteoutfile(src,dst_ds):
    xsize = src.RasterXSize   
    ysize = src.RasterYSize   
    block_xsize, block_ysize = 1000,1000
    for x in range(0,xsize,block_xsize):
        if x + block_xsize < xsize:
            cols =block_xsize
        else:
            cols=xsize-x
        for y in range(0,ysize,block_ysize):
            if y + block_ysize < ysize:
                rows = block_ysize
            else:
                rows = ysize - y
            abLAI = src.ReadAsArray(x,y,cols,rows) ###########cols列  rows行
            print(x,y)  
            ablai_accum_730=np.apply_along_axis(get_accum,0,abLAI) 
            for c in range(730):
                print(c+1)
                dst_ds.GetRasterBand(c+1).WriteArray(ablai_accum_730[c,:,:],x,y)            
    dst_ds = None

#read abLAI 
src_filename = 'E:/simulated data/EU/LAI001/abLAIblock_EU_001_730_cutsoseos.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     

#save accumulated loss
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/simulated data/EU/LAI001/abLAIb1_EU_001_cutphenology_accum.tiff', Ny,Nx,730, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)

wirteoutfile(src,dst_ds)
dst_ds = None