#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 18:30:36 2019

@author: josephzaki
"""

# ROI Functions for Getis Ord Hotspot Analysis
import numpy as np
import matplotlib.pyplot as plt
import cv2
import holoviews as hv
from holoviews import streams


def make_ROI(img, DAPI, region, vertices):
    
    # Create ROI masks to overlay over image
    ROI_masks = {}
    for vertex in range(len(vertices.data['xs'])):
        x = np.array(vertices.data['xs'][vertex]) #x coordinates
        y = np.array(vertices.data['ys'][vertex]) #y coordinates
        xy = np.column_stack((x,y)).astype('uint64') #xy coordinate pairs
        mask = np.zeros(DAPI.shape) # create empty mask
        cv2.fillPoly(mask, pts =[xy], color=255) #fill polygon
        ROI_masks[region[vertex]] = mask==255 #save to ROI masks as boolean
    xs = vertices.data['xs'][0]
    ys = vertices.data['ys'][0]

    mask = ROI_masks['ROI']
    maskedImage = np.ma.array(img, mask = ~ROI_masks['ROI'])
    xrange = np.nanargmin(maskedImage, axis=1)
    yrange = np.nanargmin(maskedImage, axis=0)
    xmin = next((i for i, x in enumerate(xrange) if x), None)
    xmax = len(xrange) - next((i for i, x in enumerate(np.flip(xrange, axis=0)) if x), None)
    ymin = next((i for i, x in enumerate(yrange) if x), None)
    ymax = len(yrange) - next((i for i, x in enumerate(np.flip(yrange, axis=0)) if x), None)
    croppedImg = img[xmin:xmax,ymin:ymax]
    mask = mask[xmin:xmax,ymin:ymax]
    maskedImage = maskedImage[xmin:xmax,ymin:ymax]
    
    
    fig1 = plt.figure(figsize=(25,15))
    plt.imshow(img*ROI_masks['ROI'], cmap='pink')
    plt.imshow(img, cmap='gist_gray', alpha=0.6)
    plt.plot([xs[-1],xs[0]],[ys[-1],ys[0]], 'ro-', alpha=0.2)
    for i in range(0, len(xs)):
        plt.plot(xs[i:i+2], ys[i:i+2], 'ro-', alpha=0.2)
    
    fig2 = plt.figure(figsize=(30,20))
    plt.subplot(121)
    plt.imshow(croppedImg, cmap='gist_gray')
    plt.subplot(122)
    plt.imshow(maskedImage, cmap='gist_gray')
    plt.title("Processed Image; Ready for Analysis")
    
    return ROI_masks, mask, croppedImg, maskedImage, fig1, fig2



# Define function that allows you to draw your ROI
def ROI_plot(reference,region_names):

    #Define parameters for plot presentation
    nobjects = len(region_names) #get number of objects to be drawn

    #Make reference image the base image on which to draw
    image = hv.Image((np.arange(reference.shape[1]), np.arange(reference.shape[0]), reference))
    image.opts(width=int(reference.shape[1]),
               height=int(reference.shape[0]),
              invert_yaxis=True,cmap='gray',
              colorbar=True,
               toolbar='above',
              title="Draw Regions: "+', '.join(region_names))

    #Create polygon element on which to draw and connect via stream to PolyDraw drawing tool
    poly = hv.Polygons([])
    poly_stream = streams.PolyDraw(source=poly, drag=True, num_objects=nobjects, show_vertices=True)
    poly.opts(fill_alpha=0.3, active_tools=['poly_draw'])
    
    return (image*poly),poly_stream
