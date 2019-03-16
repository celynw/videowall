#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
import cv2
from screeninfo import get_monitors
from PIL import Image, ImageOps
import numpy as np
from random import shuffle

#===================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("root", metavar="directory", help="Root folder where the videos are stored")
	parser.add_argument("w", metavar="width", type=int, help="Number of video columns to use")
	parser.add_argument("h", metavar="height", type=int, help="Number of video rows to use")
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
def play_videos(files, dimensions):
	# Randomise
	numToLoad = min(len(files), (args.w * args.h))
	files = files[:numToLoad]
	shuffle(files)

	windowName = "Video Wall"
	window = cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	caps = [cv2.VideoCapture(str(i)) for i in files]

	frames = [None] * (dimensions[0] * dimensions[1])
	retvals = [None] * len(files)

	while True:
		for (i, cap) in enumerate(caps):
			if (cap):
				retvals[i], frames[i] = cap.read()
		frames = [np.zeros((1920, 1080, 3), dtype="uint8") if frame is None else frame for frame in frames]
		show_combined_frames(windowName, dimensions, frames)
		if (cv2.waitKey(1) & 0xFF == ord('q')):
			break
	for cap in caps:
		if (cap):
			cap.release()

	cv2.destroyAllWindows()


#===================================================================================================
def show_combined_frames(windowName, dimensions, frames):
	"""
	Scale/crop frames so they all match exactly.
	Will run on main display.
	"""
	# TODO run once only
	m = get_monitors()[0]
	desktopSize = (m.width, m.height)

	targetW = desktopSize[0] // dimensions[0]
	targetH = desktopSize[1] // dimensions[1]

	imgs = [None] * len(frames)
	for i, frame in enumerate(frames):
		img = Image.fromarray(frame)
		imgs[i] = ImageOps.fit(img, (targetW, targetH), method=Image.LANCZOS)

	layout = list(chunks(imgs, dimensions[0]))

	rows = [None] * dimensions[1]
	for i, row in enumerate(layout):
		rows[i] = np.hstack(row)
	full = np.vstack(rows)

	cv2.imshow(windowName, full)


#===================================================================================================
def chunks(list, numElements):
	for i in range(0, len(list), numElements):
		yield list[i:i + numElements]


#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
	play_videos(files, (args.w, args.h))
