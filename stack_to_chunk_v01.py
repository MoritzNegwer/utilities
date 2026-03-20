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
input_dir = '/media/wirrbel/MN_6/2026-02-25_Workshop_4-color_nuclear/2026-03-06_ws_L_4-channel_both-side_illumination_merge/WS_L_4-channel-nuclear_stitch'
output_dir = '/media/wirrbel/MN_6/2026-02-25_Workshop_4-color_nuclear/2026-03-06_ws_L_4-channel_both-side_illumination_merge/WS_L_4-channel-nuclear_stitch_zarr'

#define thresholds. You'll need to check manually in e.g. Fiji for the ideal threshold for now. 
#TODO: Automate threshold detection with some fancy histogram-matching function
threshold_list = [200,200,105,105]

#run through channel folders 
channel_folders_list = os.listdir(input_dir)
print(channel_folders_list)

#exclude everything that isn't a folder 
channel_folders_list = [folder for folder in channel_folders_list if os.path.isdir(os.path.join(input_dir,folder))]
print(" after filtering: ",channel_folders_list)

for i,channel_name in enumerate(channel_folders_list):

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
        name="my_zarr_group",
        spatial_unit="micrometer",
        voxel_size=(1.62, 1.62, 6.0),
        array_spec=ArraySpec.from_zarr(
            zarr.empty(images.shape, chunks=(64, 64, 16), dimension_names=("x", "y", "z"))
        ),
        threshold = threshold_list[i],
    )
    print(group.levels)

    bytes_per_process = stack_to_chunk.memory_per_slab_process(images, chunk_size=4096)
    print(f"Each process will use {bytes_per_process / 1e6:.1f} MB")

    #check number of available processors 
    cpu_cores = os.cpu_count()

    group.add_full_res_data(images, n_processes=cpu_cores, threshold = threshold_list[i])

    print(group.levels)

    group.add_downsample_level(1, n_processes=cpu_cores)
    group.add_downsample_level(2, n_processes=cpu_cores)
    #group.add_downsample_level(3, n_processes=16)
    print(group.levels)

