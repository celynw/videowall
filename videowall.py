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
def play_videos(files):
	caps = [cv2.VideoCapture(str(i)) for i in files]

	frames = [None] * len(files)
	retvals = [None] * len(files)

	while True:
		for (i, cap) in enumerate(caps):
			if (cap):
				retvals[i], frames[i] = cap.read()
		for (i, frame) in enumerate(frames):
			if (retvals[i]):
				cv2.imshow(str(files[i]), frames[i])
		if (cv2.waitKey(1) & 0xFF == ord('q')):
			break
	for cap in caps:
		if (cap):
			cap.release()

	cv2.destroyAllWindows()

#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
	files = files[:2] # DEBUG
	play_videos(files)
