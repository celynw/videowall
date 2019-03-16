#!/usr/bin/env python
from stream import FileVideoStream

from argparse import ArgumentParser
from pathlib import Path
from threading import Thread
import sys
import time
import cv2
# from queue import Queue
# import imutils
# from imutils.video import FPS
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
	windowName = "Video Wall"
	window = cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

	while True:
		# Randomise on each iteration
		shuffle(files)
		caps = [None] * (dimensions[0] * dimensions[1])
		frames = [None] * len(caps)
		# retvals = [None] * len(caps)
		lastFrames = [time.time()] * len(caps)

		for i in range(0, min(len(files), len(caps))):
			# caps[i] = cv2.VideoCapture(str(files[i]))
			caps[i] = FileVideoStream(str(files[i]), queueSize=800).start()

		time.sleep(1)


		while True:
			for (i, cap) in enumerate(caps):
				if (cap):
					# retvals[i], frames[i] = cap.read()
					if cap.more():
						# grab the frame from the threaded video file stream, resize
						# it, and convert it to grayscale (while still retaining 3
						# channels)
						if ((time.time() - lastFrames[i]) < cap.frameTime):
							continue
						frames[i] = cap.read()
						lastFrames[i] = time.time()

						# frames[i] = imutils.resize(frames[i], width=450)

						# display the size of the queue on the frame
						# cv2.putText(frames[i], "Queue Size: {}".format(cap.Q.qsize()),
						# 	(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

						# show the frame and update the FPS counter
						# cv2.imshow("Frame", frames[i])
						# cv2.waitKey(1)
						# fps.update()

			# TODO replace with range
			frames = [np.zeros((1920, 1080, 3), dtype="uint8") if frame is None else frame for frame in frames]
			show_combined_frames(windowName, dimensions, frames)

			key = cv2.waitKey(1)
			if (key == ord('q')):
				finish(caps)
			elif (key == ord('r')):
				break

	finish(ok=False)


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
def finish(caps=None, ok=True):
	if (caps):
		for cap in caps:
			if (cap):
				# cap.release()
				cap.stop()
	cv2.destroyAllWindows()
	quit(ok)


#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
	play_videos(files, (args.w, args.h))

	# fvs = FileVideoStream("D:/test.webm").start()
	# time.sleep(0.5)

	# start the FPS timer
	# fps = FPS().start()

	# loop over frames from the video file stream
	# lastFrame = time.time()
	# while fvs.more():
	# 	# grab the frame from the threaded video file stream, resize
	# 	# it, and convert it to grayscale (while still retaining 3
	# 	# channels)
	# 	if ((time.time() - lastFrame) < fvs.frameTime):
	# 		continue
	# 	frame = fvs.read()
	# 	lastFrame = time.time()

	# 	# frame = imutils.resize(frame, width=450)

	# 	# display the size of the queue on the frame
	# 	cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
	# 		(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

	# 	# show the frame and update the FPS counter
	# 	cv2.imshow("Frame", frame)
	# 	cv2.waitKey(1)
	# 	fps.update()

	# stop the timer and display FPS information
	# fps.stop()
	# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
	# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

	# do a bit of cleanup
	# cv2.destroyAllWindows()
	# fvs.stop()
