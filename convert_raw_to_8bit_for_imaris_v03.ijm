/*
setMinAndMax(0, 2000);
run("Apply LUT");
setOption("ScaleConversions", true);
run("8-bit");

open("D:/2024-02-12_aav_brain_delivr_for_Roger/raw/organ_head_rawmask/slice_1024.tif");
selectImage("slice_1024.tif");
saveAs("Tiff", "D:/2024-02-12_aav_brain_delivr_for_Roger/output/RGB_tiffs/RGB_c03_test.tif");
*/
 // This section attempting to cycle through all files in a directory 

setBatchMode("hide");

//input = "D:/2024-02-12_aav_brain_delivr_for_Roger/raw/organ_head_rawmask/";
//input = "D:/2024-02-12_aav_brain_delivr_for_Roger/output/06_visualization/output/organ_head_rawmask/organ_head_rawmask_rgb_tiffs/";
input = "D:/2024-02-12_aav_brain_delivr_for_Roger/aav_run/06_visualization/output/organ_head_rawmask/organ_head_rawmask_rgb_tiffs/";
output = "D:/2024-02-12_aav_brain_delivr_for_Roger/aav_run/RGB_tiffs/";

list = getFileList(input);
for (i = 0; i < list.length; i++) {
	action(input, output, list[i],i);
}

function action (input, output, filename,z) {
	print("processing "+ String.pad(z,4));
	
	open(input+filename);
	
	/*
	//16-bit conversion to 8-bit
	setMinAndMax(0, 2000);
	run("Apply LUT");
	setOption("ScaleConversions", true);
	run("8-bit");
	run("Bio-Formats Exporter", " save=" + output+"RGB_c03_"+String.pad(z,4)+".tif" + " export compression=LZW");
	close();
	*/
	
	
	//8-bit RGB splitting
	rename("img");
	run("Split Channels");

	selectImage("img (red)");
	run("Bio-Formats Exporter", " save=" + output+"RGB_c00_"+String.pad(z,4)+".tif" + " export compression=LZW");
	close();
	
	selectImage("img (green)");
	run("Bio-Formats Exporter", " save=" + output+"RGB_c01_"+String.pad(z,4)+".tif" + " export compression=LZW");
	close();

	selectImage("img (blue)");
	run("Bio-Formats Exporter", " save=" + output+"RGB_c02_"+String.pad(z,4)+".tif" + " export compression=LZW");
	close();
		
	/*
	//compression
	selectWindow(filename);
	run("Bio-Formats Exporter", " save=" + output+filename + " export compression=LZW");
	close();
	*/

}
