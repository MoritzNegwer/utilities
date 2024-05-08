setBatchMode("hide");

list_dirs = newArray("/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/A01",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/B01-PV488_SST568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/B02-PV488_SST568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/B03-PV488_SST568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/B04-PV488_SST568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/C01-PV488-VIP568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/C02-PV488-VIP568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/C03-PV488-VIP568",
"/media/wirrbel/MN_2/2020-09-17_01_PV+SST+VIP_colabeling_PV/C04-PV488-VIP568");

for (i=0; i<= list_dirs.length; i++) {
	path_folder = list_dirs[i];
	path_filelist = getFileList(path_folder);
	//Array.print(path_filelist);
	run("Grid/Collection stitching", "type=[Unknown position] order=[All files in directory] directory="+path_folder+" output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.5 absolute_displacement_threshold=20 subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display] ");
	run("Split Channels");
	run("Merge Channels...", "c1=C3-Fused c2=C2-Fused c3=C1-Fused create ignore");
	saveAs("Tiff", path_folder+"/_composite.tif");
	close("*");
}

