# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:08:28 2024

@author: chenq4
"""

import numpy as np
import gdal
import gdalconst   

#%%calculate abLAI2018

#read LAI data
src_filename = 'E:/EU/LAI001/LAI_0418_001_eu.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     


#write output data
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAIblock_EU_001_10day.tiff', Ny,Nx,36, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)                        
                      
                    
#read in blocks

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
        Lai = src.ReadAsArray(x,y,cols,rows) 
        print(x,y)                        
                                                                    
        Laisp=np.split(Lai,15,axis=0)                       
        leaf_        =   np.array(Laisp)                                         
                        
        leaf_15=leaf_[:14,:,:,:]
        
        LAI_full_avg =  np.zeros(np.shape(leaf_15[0,:,:,:]))
        LAI_full_std =  np.zeros(np.shape(leaf_15[0,:,:,:]))

        LAI_full_avg=np.nanmean(leaf_15,0)
        LAI_full_std=np.nanstd(leaf_15,0)

        lai_2018=leaf_[14,:,:,:]
        dif=lai_2018-LAI_full_avg
        #calculate abLAI 
        with np.errstate(divide='ignore'):
            abLAI = np.where(LAI_full_std != 0., dif / LAI_full_std, 0)
        #save 
        for c in range(36):
            print(c+1)
            dst_ds.GetRasterBand(c+1).WriteArray(abLAI[c,:,:],x,y)
dst_ds = None

#%%calculate abLAI2017

#read LAI data
src_filename = 'E:/EU/LAI001/LAI_0418_001_eu.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     


#write output
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAIblock_EU_001_10day_2017.tiff', Ny,Nx,36, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)                        
                      
                    
#read in blocks

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
        Lai = src.ReadAsArray(x,y,cols,rows) 
        print(x,y)                        
                                                                    
        Laisp=np.split(Lai,15,axis=0)                       
        leaf_        =   np.array(Laisp)                                         
                        
        leaf_15=leaf_[:14,:,:,:]
        
        LAI_full_avg =  np.zeros(np.shape(leaf_15[0,:,:,:]))
        LAI_full_std =  np.zeros(np.shape(leaf_15[0,:,:,:]))

        LAI_full_avg=np.nanmean(leaf_15,0)
        LAI_full_std=np.nanstd(leaf_15,0)

        lai_2017=leaf_[13,:,:,:]
        dif=lai_2017-LAI_full_avg
        #calculate abLAI 
        with np.errstate(divide='ignore'):
            abLAI2017=np.where(LAI_full_std != 0., dif / LAI_full_std, 0)
        #save
        for c in range(36):
            print(c+1)
            dst_ds.GetRasterBand(c+1).WriteArray(abLAI2017[c,:,:],x,y)
dst_ds = None

#%%interpolation of abLAI2017 

import numpy as np
import gdal
import datetime
import calendar
import gdalconst
import pandas as pd

#read abLAI 2017
src_filename = 'E:/EU/LAI001/abLAIblock_EU_001_10day_2017.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

#save 365abLAI 2017 
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAI365block_EU_001_2017.tiff', Ny,Nx,365, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)


#define time
def getMonthFirstDayAndLastDay_c(year=None, month=None):
    L=[]
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year
    
    if month:
        month = int(month)
    else:
        month = datetime.date.today().month
    
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)
    
    firstDay = datetime.date(year=year, month=month, day=10)
    midDay=datetime.date(year=year, month=month, day=20)
    lastDay = datetime.date(year=year, month=month, day=monthRange)
    L.append(firstDay)
    L.append(midDay)
    L.append(lastDay)
    return L
def copernicus_time():
    start_year = 2017
    end_year   = 2018
    dates_interval  = []
    for year in range(start_year,end_year,1):
        interval =   np.arange(1, 13)
        
        for m in interval:
            dates_interval.extend(getMonthFirstDayAndLastDay_c(year=year, month=m))    
                
    dates_new = [datetime.datetime(2017,1,1) + datetime.timedelta(days=day) for day in range(365)]
    
    date_10=[]
    for i in dates_interval:
        d=datetime.datetime(i.year,i.month,i.day)
        date_10.append(d)
    return date_10,dates_new
#interpolation
def to365_c(yearablai):
    try:
        date_10,dates_new=copernicus_time()
        oldindexr=pd.Series(yearablai, index=date_10)
        newindex=dates_new
        dailylai=oldindexr.reindex(oldindexr.index | newindex).interpolate(method='index').loc[newindex]
        dailylai=dailylai.fillna(method='bfill')
    except:
        dailylai=np.zeros((365))
        dailylai=dailylai*np.NaN
    return dailylai 

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
        abLAI = src.ReadAsArray(x,y,cols,rows) 
        print(x,y)  
        #interpolation
        ablai365=np.apply_along_axis(to365_c,0,abLAI) 
        for c in range(365):
            print(c+1)
            dst_ds.GetRasterBand(c+1).WriteArray(ablai365[c,:,:],x,y)
dst_ds = None 
print('finished!')

#%%interpolation of abLAI2018
import numpy as np
import gdal
import gdalconst
import calendar
import pandas as pd
import datetime

#read abLAI2018
src_filename = 'E:/EU/LAI001/abLAIblock_EU_001_10day.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

#save 365abLAI 2018
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAI365block_EU_001.tiff', Ny,Nx,365, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)

#define time
def getMonthFirstDayAndLastDay_c(year=None, month=None):
    L=[]
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year
    
    if month:
        month = int(month)
    else:
        month = datetime.date.today().month
    
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)
    
    firstDay = datetime.date(year=year, month=month, day=10)
    midDay=datetime.date(year=year, month=month, day=20)
    lastDay = datetime.date(year=year, month=month, day=monthRange)
    L.append(firstDay)
    L.append(midDay)
    L.append(lastDay)
    return L

def copernicus_time():
    start_year = 2018
    end_year   = 2019
    dates_interval  = []
    for year in range(start_year,end_year,1):
        interval =   np.arange(1, 13)
        
        for m in interval:
            dates_interval.extend(getMonthFirstDayAndLastDay_c(year=year, month=m))    
                
    dates_new = [datetime.datetime(2018,1,1) + datetime.timedelta(days=day) for day in range(365)]
    
    date_10=[]
    for i in dates_interval:
        d=datetime.datetime(i.year,i.month,i.day)
        date_10.append(d)
    return date_10,dates_new
#interpolation
def to365_c(yearablai):
    try:
        date_10,dates_new=copernicus_time()
        oldindexr=pd.Series(yearablai, index=date_10)
        newindex=dates_new
        dailylai=oldindexr.reindex(oldindexr.index | newindex).interpolate(method='index').loc[newindex]
        dailylai=dailylai.fillna(method='bfill')
    except:
        dailylai=np.zeros((365))
        dailylai=dailylai*np.NaN
    return dailylai 

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
        abLAI = src.ReadAsArray(x,y,cols,rows) 
        print(x,y)  
        #interpolation
        ablai365=np.apply_along_axis(to365_c,0,abLAI) 
        for c in range(365):
            print(c+1)
            dst_ds.GetRasterBand(c+1).WriteArray(ablai365[c,:,:],x,y)
dst_ds = None 
print('finished!')

#%%merge abLAI of 2017 and 2018 
import numpy as np
import gdal
import gdalconst   

#read abLAI 2018
src_filename = 'E:/EU/LAI001/abLAI365block_EU_001.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     

#read abLAI 2017
srcc_filename = 'E:/EU/LAI001/abLAI365block_EU_001_2017.tiff'
srcc = gdal.Open(srcc_filename, gdalconst.GA_ReadOnly)
src_proj = srcc.GetProjection()
src_geotrans = srcc.GetGeoTransform()     

#write output
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAIblock_EU_001_365_1718.tiff', Ny,Nx,730, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)                        


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
        print(x,y)
        lai_2018 = src.ReadAsArray(x,y,cols,rows) 
        lai_2017 = srcc.ReadAsArray(x,y,cols,rows) 

        laiall=np.append(lai_2017,lai_2018,axis=0)

        for c in range(730):
            print(c+1)
            dst_ds.GetRasterBand(c+1).WriteArray(laiall[c,:,:],x,y)
dst_ds = None

#%% cut merged abLAI based on phenology
import numpy as np
import gdal
import gdalconst   
import pandas as pd

src_filename = 'E:/EU/LAI001/abLAIblock_EU_001_365_1718.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()     

src2_filename = 'E:/EU/LAI001/phenology_sos_001.tiff'
src2 = gdal.Open(src2_filename, gdalconst.GA_ReadOnly)
src2_proj = src2.GetProjection()
src2_geotrans = src2.GetGeoTransform()     

src3_filename = 'E:/EU/LAI001/phenology_eos_001.tiff'
src3 = gdal.Open(src3_filename, gdalconst.GA_ReadOnly)
src3_proj = src3.GetProjection()
src3_geotrans = src3.GetGeoTransform()     

#save cutted abLAI EU
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/abLAIblock_EU_001_730_cutsoseos.tiff', Ny,Nx,730, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
dst_ds.SetGeoTransform(src_geotrans)
dst_ds.SetProjection(src_proj)  


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
        ablai = src.ReadAsArray(x,y,cols,rows) 
        sos=src2.ReadAsArray(x,y,cols,rows) 
        eos=src3.ReadAsArray(x,y,cols,rows) 
        print(x,y)                        

        longestlai=np.zeros(np.shape(ablai))
        longestlai=longestlai*np.nan
        
        Nx,Ny=np.shape(sos)
        for ilat in np.arange(Nx):  
            for ilon in np.arange(Ny):
                print(ilat,ilon)
                lai=pd.Series(ablai[:,ilat,ilon])
                if np.all(np.isnan(lai)):
                    longestlai[:,ilat,ilon]=np.nan
                else:
                    try:
                       laicut=lai[int(sos[ilat,ilon]):int(eos[ilat,ilon])]
                       df = pd.DataFrame({'s1':lai, 's2':laicut})
                       laicut=df['s2']
                       longestlai[:,ilat,ilon]=laicut
                    except:
                        longestlai[:,ilat,ilon]=np.nan   
                        
        for i in range(730):
            dst_ds.GetRasterBand(i+1).WriteArray(longestlai[i,:,:],x,y)
dst_dss = None