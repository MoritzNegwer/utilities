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

def debug_replace_media (TextfileAddress):
    s = open(TextfileAddress).read()
    s, num_changes = re.subn(r'/media/',"/home/",s)
    if num_changes == 0: 
         IJ.showMessage("Tile config update error","Could not update tile config z-plane. Please check your tile config file and restart the script")
    f = open(TextfileAddress, 'w')
    f.write(s)
    f.close()

def get_max_zplane(txt_file):
	#reads the tileconfig file and tries to guess how many z-planes there are 
    try:
        with open(txt_file, 'r') as f:
            lines = f.readlines()
            if len(lines) < 5: return None 
            # Ensure file has at least 5 lines because that's where Fiji's stitching script puts the first image path
            folder = os.path.dirname(lines[4].split(';')[0].strip()) #extract the directory
        
        z_vals = []
        #get all z-plane numbers from all files in the folder 
        for filename in os.listdir(folder):
            match = re.search(r'Z(\d+)', filename)
            if match: z_vals.append(int(match.group(1)))
        
        #look for the highest z-plane number 
        return max(z_vals) if z_vals else None

    except Exception as e:
        print "Error: " + str(e)
        return None

def StitchStack(TextfileAddress,channel_name):
	#extract path + filename 
  	path, filename = os.path.split(TextfileAddress)
	#replace whatever current Z___ is with Z0000
	#updateTextFile("Z0000", TextfileAddress)
 	#load files with coordinates, then pass them into Setting 
	newFolder=TextfileAddress.replace("////", "//")

    #DEBUG: replace /media/wirrbel with /home/wirrbel
	#debug_replace_media(TextfileAddress)
	
	#get number of z-planes 
	#NumImg = get_max_zplane(TextfileAddress)

	#define stitch settings. Adapt if you need more/less stringent processing 
	Setting="layout=["+newFolder+"] channels_for_registration=[Red, Green and Blue] rgb_order=rgb fusion_method=[Linear Blending] fusion=1.5 regression=0.95 max/avg=150 absolute=350";
	#run through list of images, then process by z-plane 
	for i in range(0,1):
	  	try:
			#update TextFile so that different start numbers work
			current_plane = 'Z'+str(i).zfill(4)
			#debug 
	  		print i
			updateTextFile(current_plane,TextfileAddress)
			
			#create file name 
			filepath = path + "/" +"Manual_Stitched_"+channel_name+"_"+ current_plane + '.tif' 
			
			#skip if already exists
			if not(os.path.exists(filepath)):
		
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
				try:
					IJ.runMacro (STITCHING_MACRO, str(Setting +"|"+filepath))
				except: 
					pass
			
			#try to copy plane 1 as plane 0. This is a workaround for Miltenyi/LaVision Ultramicroscope 
			#storing the metadata in the Z=0 image, which means that directly loading the z=0 plane would load 
			#the entire stack into memory, and not just the single z-plane. There seems no scriptable way to deactivate this behaviour in Fiji. 
			#if i == 1:
			#	try:
			#		z_zero_filepath = path + "/" +"Manual_Stitched_"+channel_name+"_"+ 'Z'+str(0).zfill(4) + '.tif' 
			#		shutil.copy(filepath,z_zero_filepath)
			#	except:
			#		print "z=0 plane could not be copied, possibly it already exists"

			#Update text file with Z+1 		    
			next_plane ='Z'+str(i+1).zfill(4)
			updateTextFile(next_plane,TextfileAddress)

		except:
			#if a single plane does not work anymore, skip 
			print "skipped z-plane: " + current_plane
		
		  
#### main function ### 

#[ path to TileConfig files, channel name]
TileConfigs = [ ["/home/wirrbel/2026-08-21_BTBR_B0023_test_stitch/C00_stitch/TileConfiguration_{zzz}.txt.registered","B0023_C00_WFA-488_Z0000"],
["/home/wirrbel/2026-08-21_BTBR_B0023_test_stitch/C01_stitch/TileConfiguration_{zzz}.txt.registered","B0023_C01_TH-560_Z0000"],
["/home/wirrbel/2026-08-21_BTBR_B0023_test_stitch/C02_stitch/TileConfiguration_{zzz}.txt.registered","B0023_C02_Iba1-647_Z0000"],
["/home/wirrbel/2026-08-21_BTBR_B0023_test_stitch/C03_stitch/TileConfiguration_{zzz}.txt.registered","B0023_C03_NucSpot-750_Z0000"],
]

#single-threaded: 
for config,channel_name in TileConfigs:
	StitchStack(config,channel_name)


"""
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
"""