#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-02-07

@author: wirrbel
"""

import pathlib
import sys
import tempfile
import os
import numpy as np

import dask_image.imread
import matplotlib.pyplot as plt
import skimage.color
import skimage.data
import tifffile
import zarr
from loguru import logger
from pydantic_zarr.v3 import ArraySpec



#ugly hack to get the folder with local modifications to work
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/media/wirrbel/MN_6/2026-02-04_I9_zstacks/stack-to-chunk/src/')

import stack_to_chunk 

#define folders
#input_dir = '/media/wirrbel/MN_6/I10_stitch/I10_P0007_stitch'
#output_dir = '/media/wirrbel/MN_6/I10_stitch/I10_P0007_stitch.zarr'

input_dirs = [  #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_E0023_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0001_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0002_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0003_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0004_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0005_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0006_stitch",
                #"/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0007_stitch",
                "/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0008_stitch/",
                "/media/wirrbel/MN_7/2026-03-23_I10_Ehmt1-Pten-batch-1/I10_P0009_stitch/",
            ]

output_dirs = [ #"/media/wirrbel/MN_6/I10_stitch/I10_E0023_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0001_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0002_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0003_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0004_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0005_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0006_stitch.zarr",
                #"/media/wirrbel/MN_6/I10_stitch/I10_P0007_stitch.zarr",
                "/media/wirrbel/MN_6/I10_stitch/I10_P0008_stitch.zarr",
                "/media/wirrbel/MN_6/I10_stitch/I10_P0009_stitch.zarr",
              ]


#define thresholds. You'll need to check manually in e.g. Fiji for the ideal threshold for now. 
#TODO: Automate threshold detection with some fancy histogram-matching function
threshold_list = [220,220,120,100]

for i,input_dir in enumerate(input_dirs):
    #run through channel folders 
    channel_folders_list = os.listdir(input_dir)
    #print(channel_folders_list)

    #exclude everything that isn't a folder 
    channel_folders_list = [folder for folder in channel_folders_list if os.path.isdir(os.path.join(input_dir,folder))]
    print(" after filtering: ",channel_folders_list)

    #define output folder 
    output_dir = output_dirs[i]

    for j,channel_name in enumerate(channel_folders_list):

        print("now processing folder", channel_name)
        #define folder name 
        slice_dir = os.path.join(input_dir,channel_name)

        #pre-check images
        images = dask_image.imread.imread((slice_dir+"/*.tif")).T
        print(images)

        #Running stack-to-chunk
        logger.enable("stack_to_chunk")
        #logger.add(sys.stdout, level="INFO")

        group = stack_to_chunk.MultiScaleGroup(
            (os.path.join(output_dir, channel_name + ".ome.zarr")),
            name=channel_name,
            spatial_unit="micrometer",
            voxel_size=(1.62, 1.62, 6.0),
            array_spec=ArraySpec.from_zarr(
                zarr.empty(images.shape, chunk_shape=(64, 64, 16), dimension_names=("x", "y", "z"), zarr_format=3, dtype=images.dtype)
            ),
            threshold = threshold_list[j],
        )
        print(group.levels)

        #bytes_per_process = stack_to_chunk.memory_per_slab_process(images, chunk_size=4096)
        #print(f"Each process will use {bytes_per_process / 1e6:.1f} MB")

        #check number of available processors 
        cpu_cores = os.cpu_count()

        #generate a zarr array and add the images 
        group.add_full_res_data(images, n_processes=4, threshold = threshold_list[j])

        print(group.levels)

        #downsample_func = np.max makes the data much more visible in napari. Strictly for viewing only. (default: np.mean)
        group.add_downsample_level(1, n_processes=cpu_cores,downsample_func = np.max)
        group.add_downsample_level(2, n_processes=cpu_cores,downsample_func = np.max)
        #group.add_downsample_level(3, n_processes=16)
        print(group.levels)

