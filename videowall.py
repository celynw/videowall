#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
import cv2
from screeninfo import get_monitors
from PIL import Image, ImageOps
import numpy as np

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
	windowName = "Video Wall"
	window = cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	caps = [cv2.VideoCapture(str(i)) for i in files]

	frames = [None] * len(files)
	retvals = [None] * len(files)

	while True:
		for (i, cap) in enumerate(caps):
			if (cap):
				retvals[i], frames[i] = cap.read()
		show_combined_frames(windowName, frames)
		if (cv2.waitKey(1) & 0xFF == ord('q')):
			break
	for cap in caps:
		if (cap):
			cap.release()

	cv2.destroyAllWindows()


#===================================================================================================
def show_combined_frames(windowName, frames):
	"""
	Will run on main display
	"""
	# TODO run once only
	m = get_monitors()[0]
	desktopSize = (m.width, m.height)

	# Scale/crop frames so they all match exactly
	targetW = desktopSize[0] // len(frames)
	targetH = desktopSize[1]

	imgs = [None] * len(frames)
	for i, frame in enumerate(frames):
		img = Image.fromarray(frame)
		imgs[i] = ImageOps.fit(img, (targetW, targetH), method=Image.LANCZOS)

	combined = np.hstack(imgs)
	cv2.imshow(windowName, combined)


#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
	files = files[:2] # DEBUG
	play_videos(files)
