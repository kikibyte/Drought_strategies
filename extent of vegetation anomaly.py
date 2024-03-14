# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 18:31:53 2024

@author: chenq4
"""
import numpy as np
import gdal
import gdalconst   

def get_ablaibsum(index,threshold):
    z,x,y=np.shape(index)
    laibsum_=np.zeros([x,y])
    laibsum_=laibsum_*np.nan
    
    Nx,Ny=np.shape(laibsum_)
    for ilat in np.arange(Nx):  
        for ilon in np.arange(Ny):
            a=index[:,ilat,ilon]
            laiball_=[]
            if np.all(np.isnan(a)):
                laibsum_[ilat,ilon]=np.nan
            elif len(np.where(a<threshold)[0])==0:
                laibsum_[ilat,ilon]=np.nan   
            else:
              laibx=np.where(a<threshold)[0]
              for i in laibx:
                  laiball_.append(a[i])
              laibsum_[ilat,ilon]=np.nansum(laiball_)

    return laibsum_

def wirteoutfile(src,dst_ds,value):
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
            spei3 = src.ReadAsArray(x,y,cols,rows) 
            print(x,y)     
            #calculate extent 
            speisum=get_ablaibsum(spei3,value)
            dst_ds.GetRasterBand(1).WriteArray(speisum,x,y)
    dst_ds = None

#read cutted abLAI EU
src_filename = 'E:/simulated data/EU/LAI001/abLAIblock_EU_001_730_cutsoseos.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     
#save extent EU
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/simulated data/EU/LAI001/abLAIb1sum_EU_001_cutphenology.tiff', Ny,Nx,1, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)

wirteoutfile(src,dst_ds,value=-1)#threshold=-1
dst_ds = None
