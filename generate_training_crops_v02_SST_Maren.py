#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 22:55:54 2024

@author: wirrbel
"""

import numpy as np
import tifffile
import cv2
import os
import glob

def get_real_size(raw_folder):
    z = len([i for i in os.listdir(raw_folder) if ".tif" in i])
    img = cv2.imread(raw_folder + "/" + os.listdir(raw_folder)[0])
    y = img.shape[0]
    x = img.shape[1]
    return (z, y, x)
    

if __name__ == "__main__":
    folder_list = [["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-23_SST_P25_Sample1_57645_Het/190423_Sample1_57645_Het_TdTom_16-15-57/",
                    "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample1_57645_Het/"],
                   ["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-24_SST_P25_Sample2_57646_WT/190424_57646_WT_TdTom_11-48-51/",
                    "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/P25_Sample2_57646_WT/"],
                   ["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-25_SST_P25_Sample3_57647_WT/190425_57647_WT_TdTom_10-26-56/",
                    "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample3_57647_WT/"],
                   ["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-25_SST_P25_Sample4_57648_Het/190425_57648_Het_TdTom_14-03-14/",
                    "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample4_57648_Het/"],
                   #["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-26_SST_P25_Sample5_57654_WT/190426_57654_WT_TdTom_08-52-16/",
                   # "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample5_57654_WT/"],
                   ["/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-26_SST_P25_Sample6_57657_Het/190426_57657_Het_TdTom_14-57-21/",
                    "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample6_57657_Het/"]
                   ]
    
    for raw_folder, output_folder in folder_list:
        #define input folder
        #raw_folder = "/media/wirrbel/7024783D696D0AAE/SST_Maren/2019-04-26_SST_P25_Sample5_57654_WT/190426_57654_WT_TdTom_08-52-16/"
        
        #define output folder
        #output_folder = "/media/wirrbel/7024783D696D0AAE/training_crops/SST_Maren/Sample5_57654_WT/"
        
        #try to make the folders
        os.makedirs(output_folder,exist_ok=True)
        
        #which size should the patches have (default = 100 in each dimension)
        patch_x = 200
        patch_y = 200
        patch_z = 200
        
        #how many patches should be generated?
        patch_num = 10
        
        #define minimum threshold to avoid getting too much background
        min_thresh = 500
        
        #get dimensions 
        z,y,x = get_real_size(raw_folder)
            
        #generate image list
        img_list = sorted(glob.glob(raw_folder+"*.tif"))
        
        i = 0
        while i < patch_num:
            #generate a set of random coordinates 
            random_coordinates = np.random.randint([0,0,0],[z-patch_z,y-patch_y,x-patch_x])
            
            #load image cube at random coordinates 
            img_cube = np.zeros((patch_z,patch_y,patch_x),dtype=np.uint16)
            for z_cube,z_slice in enumerate(range(random_coordinates[0],random_coordinates[0]+patch_z)):
                img = tifffile.imread(img_list[z_slice])
                cropped = img[random_coordinates[1]:random_coordinates[1]+patch_y,random_coordinates[2]:random_coordinates[2]+patch_x]
                img_cube[z_cube] = cropped 
            
            
            #if the cube does contain more than background threshold, use it 
            if img_cube.mean() > min_thresh:
                print("loaded valid cube number ",i," at coordinates:", random_coordinates, " ,saving tiff")    
                #define name with all parameters
                filename = "training_cube_"+str(i).zfill(3)+"_dims_"+str(patch_z)+"-"+str(patch_x)+"-"+str(patch_x)+ \
                    "_starting_at_"+str(random_coordinates[0])+"-"+str(random_coordinates[1])+"-"+str(random_coordinates[2])+".tif"
                
                #write out as tiff stack
                tifffile.imwrite(os.path.join(output_folder,filename),img_cube)
                
                #TODO: also include nifti saver for compatibility with the training pipeline
                
                #increment index by 1
                i+=1 