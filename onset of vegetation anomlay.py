# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 18:01:28 2024

@author: chenq4
"""

import pandas as pd  
import numpy as np
import gdal
import gdalconst       
import multiprocessing

def fun(f, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, f(x)))

def parmap(f, X, nprocs):
    q_in = multiprocessing.Queue(1)
    q_out = multiprocessing.Queue()

    proc = [multiprocessing.Process(target=fun, args=(f, q_in, q_out))
            for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(X)]
    [q_in.put((None, None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]
    return [x for i, x in sorted(res)]

def GetMaxevent(LAIevent):        
    maks=max(LAIevent, key=lambda k: len(LAIevent[k]))
    return LAIevent[maks]

def _sign_grouper(anomalies):
    sign = np.sign(anomalies)
    sign[sign == 0] = -1
    runs = (sign != sign.shift(1)).astype(int).cumsum()
    runs[anomalies.isnull()] = np.nan
    runs = runs - (runs.min() - 1)
    return(anomalies.groupby(runs))

def get_runs(anomalies):
    return({
        name: _sign_grouper(anomalies=anomalies).get_group(name=name)
        for name in _sign_grouper(anomalies=anomalies).indices
        })

def pool_runs(runs, pooling_method='None', show_positives=False,**kwargs):
    def _sign_wo_zero(value):
        if np.sign(value) == 0:
            return(-1)
        else:
            return(np.sign(value))

    if pooling_method == 'None':
        runs_pooled = runs              
    if show_positives:
        return(runs_pooled)
    else:
        return({
            num: run
            for num, run in runs_pooled.items()
            if run.sum() < 0
            })
    
def get_longlai(lai):
    longestlai=np.zeros(730)
    longestlai=longestlai*np.nan
    if np.all(np.isnan(lai)):
        longestlai[:]=np.nan
    else:
        try:
            lairuns=get_runs(anomalies=lai-x0)
            LAIevent = pool_runs(
                        runs=lairuns,
                        pooling_method='None',
                        )
            lailong=GetMaxevent(LAIevent)-1
            df = pd.DataFrame({'s1':lai, 's2':lailong})
            lailong=df['s2']
            longestlai[:]=lailong
        except:
            longestlai[:]=np.nan   
    return longestlai

if __name__ == '__main__':
    #read abLAI
    src_filename =  'E:/EU/LAI001/abLAIblock_EU_001_730_cutsoseos.tiff'
    srcc = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
    src_proj = srcc.GetProjection()
    src_geotrans = srcc.GetGeoTransform()
    #save longest ALAI event EU
    Nx,Ny=2500,4000
    drv = gdal.GetDriverByName("GTIFF")
    dst_dss = drv.Create('E:/EU/LAI001/longestLAIevent_001_730_phenology.tiff', Ny,Nx,730, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","BIGTIFF=YES","COMPRESS=LZW"])
    dst_dss.SetGeoTransform(src_geotrans)
    dst_dss.SetProjection(src_proj)

    x0=pd.Series(list(range(730)))
    x0= x0.copy() * np.nan
    x0[:]=-1
    #read in blocks    
    xsize = srcc.RasterXSize   
    ysize = srcc.RasterYSize    
    block_xsize, block_ysize = 4000,100
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
            ablai = srcc.ReadAsArray(x,y,cols,rows) 
            print(x,y)                        
                            
            longestlai_=np.zeros(np.shape(ablai))
            longestlai_=longestlai_*np.nan
            
            Nz,Nx,Ny=np.shape(ablai)
            for ilat in np.arange(Nx):  
                Inputs = []
                for ilon in np.arange(Ny):
                    print(x,y,ilat,ilon)
                    lai=pd.Series(ablai[:,ilat,ilon])
                    Inputs.append(lai)
                ret = parmap(get_longlai, Inputs, nprocs=4)
                longestlai_[:,ilat,:] = np.array(np.transpose(np.array(ret),axes=[1,0]))
            for i in range(730):
                print(i+1)
                dst_dss.GetRasterBand(i+1).WriteArray(longestlai_[i,:,:],x,y)
    dst_dss = None
    print('finished one!')
    
#%%get onset from longest ALAI event
import pandas as pd
import numpy as np
import gdal
import gdalconst    

#read longest ALAI event
src_filename = 'E:/EU/LAI001/longestLAIevent_001_730_phenology.tiff'
src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()
#save onset EU
Nx,Ny=2500,4000
drv = gdal.GetDriverByName("GTIFF")
dst_ds = drv.Create('E:/EU/LAI001/longestLAI_onset_001_phenology.tiff', Ny,Nx,1, gdal.GDT_Float32,options=[ "INTERLEAVE=BAND", "TILED=YES","COMPRESS=LZW"])
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
        longestlai = src.ReadAsArray(x,y,cols,rows) 
        print(x,y)    
        
        Nz,Nx,Ny=np.shape(longestlai)
        lonset=np.zeros((Nx,Ny))
        lonset=lonset*np.nan

        
        for ilat in np.arange(Nx):  
            for ilon in np.arange(Ny):        
                onellai=longestlai[:,ilat,ilon]
                if np.all(np.isnan(onellai)):
                    lonset[ilat,ilon]=np.nan
                elif not np.any(onellai):
                    lonset[ilat,ilon]=np.nan
                else:
                    lonset[ilat,ilon]=np.argwhere(np.isfinite(onellai))[0][0]   
        dst_ds.GetRasterBand(1).WriteArray(lonset,x,y)
dst_ds = None
print('finished all!')

