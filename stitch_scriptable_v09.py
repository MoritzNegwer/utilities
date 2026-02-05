from ij import IJ
from ij import ImagePlus
from ij.macro import MacroRunner
import string
from ij.io import FileSaver 
from loci.plugins.in import ImagePlusReader,ImporterOptions,ImportProcess
import sys
from ij.gui import GenericDialog
from ij.io import OpenDialog 
import os
import re
# read in and display ImagePlus object(s)
from loci.plugins import BF
import threading
import time

def updateTextFile(z_plane,TextfileAddress):
	#updates the TextFile with the next z-plane
	#assumes that next_plane is already a string with "Z0000" or so
    s = open(TextfileAddress).read()
    s, num_changes = re.subn(r'Z\d\d\d\d',z_plane,s)
    if num_changes == 0: 
         IJ.showMessage("Tile config update error","Could not update tile config z-plane. Please check your tile config file and restart the script")
    f = open(TextfileAddress, 'w')
    f.write(s)
    f.close()


def StitchStack(TextfileAddress,channel_name,NumImg):
	#extract path + filename 
  	path, filename = os.path.split(TextfileAddress)
	#replace whatever current Z___ is with Z0000
	updateTextFile("Z0000", TextfileAddress)
 	#load files with coordinates, then pass them into Setting 
	newFolder=TextfileAddress.replace("////", "//")
	#define stitch settings. Adapt if you need more/less stringent processing 
	Setting="layout=["+newFolder+"] channels_for_registration=[Red, Green and Blue] rgb_order=rgb fusion_method=[Linear Blending] fusion=1.5 regression=0.5 max/avg=5 absolute=50";
	#run through list of images, then process by z-plane 
	for i in range(1,NumImg):
	  	try:
			#update TextFile so that different start numbers work
			current_plane = 'Z'+str(i).zfill(4)
			#debug 
	  		print i
			updateTextFile(current_plane,TextfileAddress)
			
			#create file name 
			filepath = path + "/" +"Manual_Stitched_"+channel_name+"_"+ current_plane + '.tif' 
			
			#Stitch inside an ImageJ macro (to be able to run without rendering each image)
			STITCHING_MACRO = """ 
            setBatchMode(true);
			Arguments = getArgument();
			print(Arguments);
			splitArguments = split(Arguments,"|");
			Setting = splitArguments[0];
			filepath = splitArguments[1];
				run("Stitch Collection of Images", Setting);
				selectWindow("Stitched Image");
				run("Bio-Formats Exporter", " save=" + filepath + " export compression=LZW");
				close();
				"""
			
			IJ.runMacro (STITCHING_MACRO, str(Setting +"|"+filepath))
			
			#Update text file with Z+1 		    
			next_plane ='Z'+str(i+1).zfill(4)
			updateTextFile(next_plane,TextfileAddress)
	
		except:
			#if a single plane does not work anymore, skip 
			print "skipped z-plane: " + current_plane
		
		  
#### main function ### 

#[ path to TileConfig files, channel name]
TileConfigs = [ ["/media/wirrbel/MN_6/2026-02-04_I9_zstacks/I9_right_zstack_stitch/I9_SE_C00_WFA_right_zstack/TileConfiguration_{zzz}.txt.registered","C00_WFA",954],
				["/media/wirrbel/MN_6/2026-02-04_I9_zstacks/I9_right_zstack_stitch/I9_SE_C01_NET_right_zstack/TileConfiguration_{zzz}.txt.registered","C01_NET",954],
				["/media/wirrbel/MN_6/2026-02-04_I9_zstacks/I9_right_zstack_stitch/I9_SE_C02_ChAT_right_zstack/TileConfiguration_{zzz}.txt.registered","C02_ChAT",954],
				["/media/wirrbel/MN_6/2026-02-04_I9_zstacks/I9_right_zstack_stitch/I9_SE_C03_NucSpot_right_zstack/TileConfiguration_{zzz}.txt.registered","C03_NucSpot",954],
                
				]


#run sequentially through the stack (multiprocessing is troublesome, skips images)
for config,channel_name,NumImg in TileConfigs:
	StitchStack(config,channel_name,NumImg)

''''
#start multiple threads, one for each stack
threads = []
for config,channel_name,NumImg in TileConfigs:
	t = threading.Thread(target=StitchStack, args=(config,channel_name,NumImg))
	threads.append(t)
	
# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()
'''