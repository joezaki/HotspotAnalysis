#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 19:30:16 2019

@author: josephzaki
"""

# Plotting Functions for Getis Ord Hotspot Analysis
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Plots a given image with the ROI and Z-score labeled
def PlotGetis (img,x,y,nx,ny,Zi):
    plt.figure(figsize=(8,8))
    plt.imshow(img,cmap='gist_gray')
    plt.hlines(y=x+nx, xmin=y - ny, xmax=y + ny, color='r', linestyle='dashed', linewidth=1)
    plt.hlines(y=x-nx, xmin=y - ny, xmax=y + ny, color='r', linestyle='dashed', linewidth=1)
    plt.vlines(x=y+ny, ymin=x - nx, ymax=x + nx, color='r', linestyle='dashed', linewidth=1)
    plt.vlines(x=y-ny, ymin=x - nx, ymax=x + nx, color='r', linestyle='dashed', linewidth=1)
    plt.text(x=y,y=x,s=str(Zi), horizontalalignment='center', verticalalignment='center', fontweight='bold', c='skyblue')
    plt.show()



# Plots the stats associated with a Getis analysis of an image as either "Gstat" or "Hotspot"
def statsPlot(stats, img, plotType, withImage=True):
    fig = plt.figure(figsize=(25,15), dpi=100)
    ax = plt.axes([0,0,1,1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    if withImage:
        plt.imshow(img, cmap='gist_gray')
    else:
        plt.axes().set_aspect('equal')
        plt.ylim(img.shape[0],0)
    # Drawing paramters
    mrk = 'o'
    #cl = 'darkred'
    #style = ':'
    #width = 1.5
    alpha = 0.5
    mew = 0
    for g in range(stats.shape[0]):
        x = stats['x'][g]
        y = stats['y'][g]
        nx = stats['nx'][g]
        ny = stats['ny'][g]
        Zi = stats['Z-Score'][g]
        if plotType == "Gstat":
            mrksz = np.abs(Zi)/np.log2(stats.shape[0])*2
            if stats['Sign'][g] == "+":
                plt.plot(y,x,marker='o',color='salmon', markersize=mrksz, alpha=0.5, markeredgewidth=mew)
            elif stats['Sign'][g] == "-":
                plt.plot(y,x,marker='o',color='lightblue', markersize=mrksz, alpha=0.5, markeredgewidth=mew)
            plt.text(y,x,
                     s=int(Zi), color='black', fontsize=mrksz/2,
                     horizontalalignment='center', verticalalignment='center', fontweight='bold')
        elif plotType == "Hotspot":
            mrksz = np.sqrt(nx*ny)/2
            if Zi > (np.mean(stats['Z-Score']) + np.std(stats['Z-Score'])):
                plt.plot(y,x,marker=mrk,color='firebrick', markersize=mrksz, alpha=alpha, markeredgewidth=mew)
            elif Zi > (np.mean(stats['Z-Score']) + np.std(stats['Z-Score'])/2):
                plt.plot(y,x,marker=mrk,color='coral', markersize=mrksz, alpha=alpha, markeredgewidth=mew)
            elif Zi < (np.mean(stats['Z-Score']) - np.std(stats['Z-Score'])):
                plt.plot(y,x,marker=mrk,color='dodgerblue', markersize=mrksz, alpha=alpha, markeredgewidth=mew)
            elif Zi < (np.mean(stats['Z-Score']) - np.std(stats['Z-Score'])/2):
                plt.plot(y,x,marker=mrk,color='lightskyblue', markersize=mrksz, alpha=alpha, markeredgewidth=mew)
            else:
                plt.plot(y,x,marker=mrk,color='antiquewhite', markersize=mrksz, alpha=alpha, markeredgewidth=mew)
            plt.text(y,x,
                     s=int(Zi), color='black', fontsize=mrksz/2,
                     horizontalalignment='center', verticalalignment='center', fontweight='bold')
        #plt.hlines(y=x+nx, xmin=y - ny, xmax=y + ny, color=cl, linestyle=style, linewidth=width, alpha=alpha)
        #plt.hlines(y=x-nx, xmin=y - ny, xmax=y + ny, color=cl, linestyle=style, linewidth=width, alpha=alpha)
        #plt.vlines(x=y+ny, ymin=x - nx, ymax=x + nx, color=cl, linestyle=style, linewidth=width, alpha=alpha)
        #plt.vlines(x=y-ny, ymin=x - nx, ymax=x + nx, color=cl, linestyle=style, linewidth=width, alpha=alpha)
    return fig



# Plots analyzed image as a heatmap of Z-scores
def HeatmapPlot(zs):
    # Plots the z-scores as a pixelated heatmap of the original masked image
    HeatmapPlot = plt.figure(figsize=(25,15))
    plt.imshow(zs, cmap='Spectral_r')
    plt.title("Z-scores")
    plt.colorbar()
    return HeatmapPlot



# Plots heatmap of Z-Scores with Distributions across DV and ML axes
def DV_ML_Plot(stats, zs, MLaxisZs, DVaxisZs, direction):
    
    DV_ML_Plot = plt.figure(figsize=(15, 15))
    DV_ML_Plot.set_facecolor('white')
    grid = plt.GridSpec(3, 3)
    main_ax = DV_ML_Plot.add_subplot(grid[:-1, 1:])
    y_hist = DV_ML_Plot.add_subplot(grid[:-1, 0], sharey=main_ax)
    x_hist = DV_ML_Plot.add_subplot(grid[-1, 1:], sharex=main_ax)
    
    if (direction == 'r') or (direction == 'R'):
        rightText = "Lateral"
        leftText = "Medial"
    elif (direction == 'l') or (direction == 'L'):
        rightText = "Medial"
        leftText = "Lateral"
    else:
        raise Exception("No proper direction specified. Proper directions include 'L' or 'l' for left; 'R' or 'r' for right")
    
    # image on the main axes
    main_ax.imshow(zs, cmap='Spectral_r')
    main_ax.text(zs.shape[1]/4*3, 0, s='Dorsal', color='black', fontsize=20)
    main_ax.text(zs.shape[1]/4*3, zs.shape[0], s='Ventral', color='black', fontsize=20)
    main_ax.text(zs.shape[1], zs.shape[0]/2, s=rightText, color='black', fontsize=20)
    main_ax.text(-zs.shape[1]/4, zs.shape[0]/2, s=leftText, color='black', fontsize=20)
    main_ax.axis('off')

    # histogram on the attached axes
    x_hist.fill_between(np.arange(0, len(MLaxisZs)),MLaxisZs,0, color='steelblue', alpha=0.5)
    x_hist.set_frame_on(False)
    x_hist.set_xticklabels([])
    x_hist.tick_params(bottom=False)
    x_hist.yaxis.tick_right()

    y_hist.fill_betweenx(np.arange(0, len(DVaxisZs)),DVaxisZs,0, color='darkred', alpha=0.5)
    y_hist.set_frame_on(False)
    y_hist.set_yticklabels([])
    y_hist.tick_params(left=False)
    #y_hist.xaxis.tick_top()
    y_hist.invert_xaxis()

    return DV_ML_Plot



# Plot image broken up into quadrants, with their respective Z-score distributions plotted on the right
def QuadrantPlot(stats, img, DL, VL, DM, VM):    
    QuadrantPlot = plt.figure(figsize=(15,10), dpi=100)
    plt.subplot(121)
    plt.scatter(DM[['y']],DM[['x']], s=5, c='paleturquoise', alpha=0.7, marker='*')
    plt.scatter(VM[['y']],VM[['x']], s=5, c='lightsalmon', alpha=0.7, marker='*')
    plt.scatter(DL[['y']],DL[['x']], s=5, c='steelblue', alpha=0.7, marker='*')
    plt.scatter(VL[['y']],VL[['x']], s=5, c='firebrick', alpha=0.7, marker='*')
    plt.imshow(img, cmap='gist_gray')
    plt.plot(img.shape[1]/2,img.shape[0]/2, 'ro')
    plt.hlines(img.shape[0]/2, xmin=1, xmax=img.shape[1]-1, colors='red', linestyles=':')
    plt.vlines(img.shape[1]/2, ymin=1, ymax=img.shape[0]-1, colors='red', linestyles=':')
    
    plt.subplot(122)
    plt.hist(DM['Z-Score'], bins=50, alpha=0.5, label='DM', color='paleturquoise')
    plt.hist(VM['Z-Score'], bins=50, alpha=0.5, label='VM', color='lightsalmon')
    plt.hist(DL['Z-Score'], bins=50, alpha=0.5, label='DL', color='steelblue')
    plt.hist(VL['Z-Score'], bins=50, alpha=0.5, label='VL', color='firebrick')

    plt.legend(loc='center')
    return QuadrantPlot



# Plot histogram and density of z-scores from Getis analysis
def ZdistributionPlot(stats, name):
    ZdistributionPlot = plt.figure(figsize=(20,10))
    sns.distplot(stats['Z-Score'], hist=True, 
                 bins=int(len(stats['Z-Score'])/10), color = 'slategrey',
                 hist_kws={'edgecolor':'black'})
    plt.title((name + " Z-Scores of Data"))
    plt.ylabel("Frequency")
    #return ZdistributionPlot