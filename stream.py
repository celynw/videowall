#!/usr/bin/env python
from threading import Thread
import cv2
from queue import Queue

#===================================================================================================
class FileVideoStream:
	#-----------------------------------------------------------------------------------------------
	def __init__(self, path, queueSize=128, loop=False):
		# Initialize the file video stream and the boolean indicator for stopping the thread
		self.path = path
		self.loop = loop
		self.stream = cv2.VideoCapture(path)
		self.fps = self.stream.get(cv2.CAP_PROP_FPS)
		self.frameTime = 1.0 / self.fps
		self.stopped = False
		# Initialize the queue used to store frames read from the video file
		self.Q = Queue(maxsize=queueSize)

	#-----------------------------------------------------------------------------------------------
	def start(self):
		# Start a thread to read frames from the file video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	#-----------------------------------------------------------------------------------------------
	def update(self):
		while True:
			# If the thread indicator variable is set, stop the thread
			if (self.stopped):
				return
			# Otherwise, ensure the queue has room in it
			if not (self.Q.full()):
				# Read the next frame from the file
				(grabbed, frame) = self.stream.read()
				# If the 'grabbed' boolean is False, then we have reached the end of the video file
				if not (grabbed):
					if (self.loop):
						self.reset()
					else:
						self.stop()
						return
			# Add the frame to the queue
			self.Q.put(frame)

	#-----------------------------------------------------------------------------------------------
	def read(self):
		# Return next frame in the queue
		return self.Q.get()

	#-----------------------------------------------------------------------------------------------
	def more(self):
		# Return True if there are still frames in the queue
		return self.Q.qsize() > 0

	#-----------------------------------------------------------------------------------------------
	def stop(self):
		# Indicate that the thread should be stopped
		self.stopped = True

	#-----------------------------------------------------------------------------------------------
	def reset(self):
		self.stream = cv2.VideoCapture(self.path)


#===================================================================================================
if (__name__=="__main__"):
	print("This is not supposed to be called directly")
