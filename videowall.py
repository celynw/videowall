#!/usr/bin/env python
from argparse import ArgumentParser
import numpy as np
import cv2
from pathlib import Path

#===================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("root", metavar="directory", help="Root folder where the videos are stored")
	args = parser.parse_args()
	return args


#===================================================================================================
def get_files(*args):
	args = dict(args)
	root = Path(args["root"])
	if not root.exists():
		print("Directory '{}' not found".format(root))
		quit(1)

	filetypes = [
			"*.mp4",
			"*.webm"]
	allFiles = []
	for filetype in filetypes:
		files = root.glob(filetype)
		allFiles.extend(files)

	return allFiles


#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
