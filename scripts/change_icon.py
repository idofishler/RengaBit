#!/usr/bin/python

from AppKit import NSBitmapImageRep, NSWorkspace, NSPNGFileType, NSImage
import sys
import Image
import os

renga_icon_path = os.path.expanduser("~/.cg/RengaBitIcon.png")

def extract_icon(file_path):
	file_icon_tiff = NSWorkspace.sharedWorkspace().iconForFile_(file_path).TIFFRepresentation()
	file_icon_png = NSBitmapImageRep.imageRepWithData_(file_icon_tiff).representationUsingType_properties_(NSPNGFileType, None)
	file_icon_png_path = file_path+".png"
	file_icon_png.writeToFile_atomically_(file_icon_png_path, None)
	return file_icon_png_path

def match_images(background, foreground):
	width = background.size[0]
	hight = background.size[1]
	img = foreground.resize((width, hight))
	x = 0
	y = 0
	return img, x, y

def add_rengabit_icon(fileimage):
	background = Image.open(fileimage)
	foreground = Image.open(renga_icon_path)
	img, x, y = match_images(background, foreground)
	background.paste(img, (x, y), img)
	new_icon_path = fileimage+"_new.png"
	background.save(new_icon_path)
	return new_icon_path

def set_file_icon(org_file_path, icon_img_path):
	icon_img = NSImage.alloc().init().initByReferencingFile_(icon_img_path)
	NSWorkspace.sharedWorkspace().setIcon_forFile_options_(icon_img, org_file_path, 0)

def clean(*files):
	for path in files:
		os.remove(path)
	

if __name__ == "__main__":
	usage = "Usage: {0} file_full_path".format(sys.argv[0])
	if len(sys.argv) < 2:
		print usage
		sys.exit(1)
	if not os.path.exists(sys.argv[1]):
		print "{0}: file {1} does not exists".format(*sys.argv)
		sys.exit(2)
	org_file_path = os.path.expanduser(sys.argv[1])
	org_file_img_path = extract_icon(org_file_path)
	new_img_path = add_rengabit_icon(org_file_img_path)
	set_file_icon(org_file_path, new_img_path)
	clean(org_file_img_path, new_img_path)