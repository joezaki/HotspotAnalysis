import os
import numpy as np
import cv2
from skimage.measure import block_reduce
from AnalysisFunctions import *
from ROIFunctions import *
from PlottingFunctions import *

def loadImagesROIs(filesDir):
    imgDir = (filesDir + 'Images/')
    roiDir = (filesDir + 'ROIs/')
    
    images = os.listdir(imgDir)
    ROIs = os.listdir(roiDir)
    
    if len(images) == len(ROIs):
        pass
    else:
        raise Exception("Lengths of image and ROI folders don't match. Make sure the correct file structure is met.")
    
    for i in range(len(images)):
        if images[i].split('.')[0] == images[i].split('.')[0]:
            continue
        else:
            raise Exception("There is a mismatch between images and ROI names. Make sure the correct file structure is met.")
    return images, ROIs



def BatchHotspot(filesDir, images, ROIs, threshold, downsample, nx, ny):

    for i in range(len(images)):
        os.chdir(filesDir)
        # Load image and set names
        img = cv2.imread('./Images/' + images[i])[:,:,0]
        name = images[i].split('_img.')[0] + "_" + str(nx) + "x" + str(ny)
        if downsample:
            bitdepth = type(img)
            img = block_reduce(img, (2,2), np.mean).astype(bitdepth)

        # Remove saturated pixels
        avgPixel = np.mean(img)
        img[img > threshold] = avgPixel

        # Use ROI to created masked image
        mask = cv2.imread('./ROIs/' + ROIs[i])[:,:,0].astype(bool)
        maskedImage = np.ma.array(img, mask = ~mask)
        xrange = np.nanargmin(maskedImage, axis=1)
        yrange = np.nanargmin(maskedImage, axis=0)
        xmin = next((i for i, x in enumerate(xrange) if x), None)
        xmax = len(xrange) - next((i for i, x in enumerate(np.flip(xrange, axis=0)) if x), None)
        ymin = next((i for i, x in enumerate(yrange) if x), None)
        ymax = len(yrange) - next((i for i, x in enumerate(np.flip(yrange, axis=0)) if x), None)
        croppedImg = img[xmin:xmax,ymin:ymax]
        mask = mask[xmin:xmax,ymin:ymax]
        maskedImage = maskedImage[xmin:xmax,ymin:ymax]

        # Run Getis analysis and save stats and necessary variables for visualizations
        stats = Getis(mask, maskedImage, nx, ny)
        direction, zs, DL, VL, DM, VM, MLaxisZs, DVaxisZs, quadrantStds = processedStats(stats, maskedImage, name)
        
        
        # Create new folder for images
        path = "./" + name
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)
        os.chdir(path)
        
        # Create and save visualizations in new folder
        Heatmap = HeatmapPlot(zs)
        Heatmap.savefig(((name + "_HeatmapPlot.pdf")), bbox_inches="tight")
        plt.close(Heatmap)
        DV_ML = DV_ML_Plot(stats, zs, MLaxisZs, DVaxisZs, direction)
        DV_ML.savefig(((name + "_DV_ML_Plot.pdf")), bbox_inches="tight")
        plt.close(DV_ML)
        Quadrant = QuadrantPlot(stats, maskedImage, DL, VL, DM, VM)
        Quadrant.savefig(((name + "_QuadrantPlot.pdf")), bbox_inches="tight")
        plt.close(Quadrant)
        Gstat = statsPlot(stats, maskedImage, "Gstat")
        Gstat.savefig(((name + "_GstatPlot.pdf")), bbox_inches="tight")
        plt.close(Gstat)
        Hotspot = statsPlot(stats, maskedImage, "Hotspot")
        Hotspot.savefig(((name + "_HotspotPlot.pdf")), bbox_inches="tight")
        plt.close(Hotspot)
        Zdistribution = ZdistributionPlot(stats, name)
        Zdistribution.savefig(((name + "_ZdistributionPlot.pdf")), bbox_inches="tight")
        plt.close(Zdistribution)
        
        # Save statistics in new folder
        exportStats = stats.to_csv((name + "_GetisOrdStats.csv"))
        
        # Delete current variables from memory
        del name, direction, avgPixel, img, mask, maskedImage, xrange, yrange, xmin, xmax, ymin, ymax, croppedImg, exportStats, Heatmap, DV_ML, Quadrant, Gstat, Hotspot, Zdistribution
