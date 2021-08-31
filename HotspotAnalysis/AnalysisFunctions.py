#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 19:27:41 2019

@author: josephzaki
"""

# Analysis Functions for Getis Ord Hotspot Analysis
import czifile
import os
import cv2
import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm import tqdm_notebook

# Load image file based on file type
def loadImage(imgPath, imgName, img_channel=1, DAPI_channel=0):
    if imgName.split(".")[1] == 'czi':
        image = czifile.imread(os.path.join(imgPath, imgName))
        DAPI = image[0,DAPI_channel,0,0,:,:,0]
        img  = image[0,img_channel,0,0,:,:,0]

    elif imgName.split(".")[1] == 'tif' or imgName.split(".")[1] == 'tiff':
        image = cv2.imread(os.path.join(imgPath, imgName))
        DAPI = image[:,:,DAPI_channel]
        img  = image[:,:,img_channel]
    else:
        raise Exception("Image file is not of an appropriate file format for hotspot analysis (i.e. TIFF or CZI)")
    return img, DAPI


# Creates n by m binned matrix of data
def submatsum(data,n,m):
    # return a matrix of shape (n,m)
    bs = data.shape[0]//n,data.shape[1]//m  # blocksize averaged over
    return np.reshape(np.array([np.sum(data[k1*bs[0]:(k1+1)*bs[0],k2*bs[1]:(k2+1)*bs[1]])
                                for k1 in range(n) for k2 in range(m)]),(n,m))



# Pulls out matrix of neighbors based on location and nx&ny size
def neighbours(im, x, y, nx, ny):
    ans = im[max(x-nx, 0):min(x+nx+1, im.shape[0]), \
             max(y-ny, 0):min(y+ny+1, im.shape[1])]
    return ans



# Getis function: Calculates Gi* statistic for all neighborhoods in an image ROI
def Getis(mask, maskedImage, nx, ny):
    stats = pd.DataFrame({'x':[],'y':[],'nx':[],'ny':[],
                          'Gi':[],'Mean':[],'Variance':[],'SD':[],
                          'Z-Score':[],'p-value':[],'Sign':[]})
    maskedImage = maskedImage.astype(float)
    im = maskedImage.copy()
    n = np.sum(mask, dtype=float)
    # Iterate through each neighborhood
    coords = [[]]
    for x in np.arange(nx,im.shape[0] - (int(nx/2)),nx):
        for y in np.arange(ny,im.shape[1] - (int(ny/2)),ny):
            isValid = neighbours(mask, x, y, int(nx/2), int(ny/2))
            # Get G statistic for this neighborhood
            if np.sum(isValid) == isValid.size:
                coords.append((x,y))
            else:
                continue
    for coord in tqdm_notebook(coords[1:], desc='Processing neighborhoods:'):
        x = coord[0]
        y = coord[1]
        wdxj = neighbours(im, x, y, int(nx/2), int(ny/2))
        Sxj = np.sum(im)
        Gi = np.sum(wdxj) / Sxj
        Yi1 = Sxj / n
        Sxj2 = np.sum(im**2)
        Yi2 = Sxj2 / n - Yi1**2
        Wi = wdxj.size
        EGi = Wi / n
        Var = Wi*(n - Wi)*Yi2 / ((n**2)*(n - 1)*(Yi1**2))
        Zi = (Gi - EGi) / np.sqrt(Var)
        p = st.norm.pdf(Zi)
        if Zi >= 0:
            sign = "+"
        else:
            sign = "-"
        stat = pd.DataFrame({'x':[x], 'y':[y], 'nx':[nx], 'ny':[ny],
                             'Gi':[np.round(Gi,10)], 'Mean':[np.round(Yi1,10)],
                             'Variance' : [np.round(Var,10)], 'SD':[np.round(np.sqrt(Var),10)],
                             'Z-Score':[np.round(Zi,10)], 'p-value':[np.round(p,20)], 'Sign':[sign]})
        stats = stats.append(stat, ignore_index=True)
    return stats



def processedStats(stats, img, name):
    direction = name.split("section")[1][2]
    zs = stats.pivot('x','y','Z-Score').values
    
    # Break ROI down to DM, VM, DL, VL compartments of striatum
    hmidline = img.shape[0]/2
    vmidline = img.shape[1]/2
    if (direction == 'r') or (direction == 'R'):
        DL = stats[(stats['y'] > vmidline) & (stats['x'] < hmidline)]
        VL = stats[(stats['y'] > vmidline) & (stats['x'] > hmidline)]
        DM = stats[(stats['y'] < vmidline) & (stats['x'] < hmidline)]
        VM = stats[(stats['y'] < vmidline) & (stats['x'] > hmidline)]
    elif (direction == 'l') or (direction == 'L'):
        DM = stats[(stats['y'] > vmidline) & (stats['x'] < hmidline)]
        VM = stats[(stats['y'] > vmidline) & (stats['x'] > hmidline)]
        DL = stats[(stats['y'] < vmidline) & (stats['x'] < hmidline)]
        VL = stats[(stats['y'] < vmidline) & (stats['x'] > hmidline)]
    else:
        raise Exception("No proper direction specified. Proper directions include 'L' or 'l' for left; 'R' or 'r' for right")
    
    # Calculate Z-scores across the DV and ML axis separately
    DVaxisZs = []
    for i in np.sort(stats.x.unique()):
        row = stats[stats['x']==i]['Z-Score']
        DVaxisZs = np.append(DVaxisZs, np.sum(row)/len(row))
    MLaxisZs = []
    for i in np.sort(stats.y.unique()):
        col = stats[stats['y']==i]['Z-Score']
        MLaxisZs = np.append(MLaxisZs, np.sum(col)/len(col))
    
    # Calculate standard deviation of Z-scores for each quadrant
    quadrants = pd.DataFrame(['DM', 'VM', 'DL', 'VL'], columns=['Quadrant'])
    stds =pd.DataFrame([np.std(DM['Z-Score']), np.std(VM['Z-Score']), np.std(DL['Z-Score']), np.std(VL['Z-Score'])], columns=['SD'])
    quadrantStds = pd.concat([quadrants, stds], axis=1)
    
    return direction, zs, DL, VL, DM, VM, MLaxisZs, DVaxisZs, quadrantStds
