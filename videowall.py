#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from random import shuffle
import sys
import vlc

#===================================================================================================
class Frame():
	#-----------------------------------------------------------------------------------------------
	def __init__(self, widgetParent, path):
		self.videoFrame = QtWidgets.QFrame()
		widgetParent.addWidget(self.videoFrame)
		# Cannot loop indefinitely (e.g. =-1)
		self.vlcInstance = vlc.Instance(['--video-on-top', "--input-repeat=65535"])
		self.videoPlayer = self.vlcInstance.media_player_new()
		self.videoPlayer.video_set_mouse_input(True)
		self.videoPlayer.video_set_key_input(True)
		# self.videoPlayer.audio_set_mute(True)
		self.videoPlayer.set_media(self.vlcInstance.media_new(str(path)))
		if sys.platform.startswith('linux'): # for Linux using the X Server
			self.videoPlayer.set_xwindow(self.videoFrame.winId())
		elif sys.platform == "win32": # for Windows
			self.videoPlayer.set_hwnd(self.videoFrame.winId())
		elif sys.platform == "darwin": # for MacOS
			self.videoPlayer.set_nsobject(int(self.videoFrame.winId()))

		self.videoPlayer.play()


#===================================================================================================
class MainWindow(QtWidgets.QMainWindow):
	keyPressed = QtCore.pyqtSignal(int)
	paused = False
	#-----------------------------------------------------------------------------------------------
	def __init__(self, files, size, *args, **kwargs):
		super().__init__(*args, **kwargs)
		shuffle(files)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.move(0, 0)
		self.resize(1920, 1080)
		self.show()
		mainFrame = QtWidgets.QFrame()
		self.setCentralWidget(mainFrame)
		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)

		self.frames = []
		file = 0
		for row in range(size[1]):
			layoutRow = QtWidgets.QHBoxLayout()
			layoutRow.setContentsMargins(0, 0, 0, 0)
			for col in range(size[0]):
				file += 1
				if (file < len(files)):
					self.frames.append(Frame(layoutRow, files[file]))
			layout.addLayout(layoutRow)
		mainFrame.setLayout(layout)
		self.keyPressed.connect(self.on_key)
		self.show()

	#-----------------------------------------------------------------------------------------------
	def keyPressEvent(self, event):
		super().keyPressEvent(event)
		self.keyPressed.emit(event.key())

	#-----------------------------------------------------------------------------------------------
	def on_key(self, key):
		if (key == QtCore.Qt.Key_Escape) or (key == QtCore.Qt.Key_Q):
			# app.quit(0)
			QtCore.QCoreApplication.quit()
		elif (key == QtCore.Qt.Key_Space):
			self.paused = not self.paused
			for frame in self.frames:
				frame.videoPlayer.set_pause(self.paused)
		else:
			print(f"Key pressed: {key}")


#===================================================================================================
def get_files(*args):
	args = dict(args)
	root = Path(args["root"])
	if not root.exists():
		print(f"Directory '{root}' not found")
		quit(1)

	filetypes = [
		"*.mp4",
		"*.webm"
	]
	allFiles = []
	for filetype in filetypes:
		files = root.glob(filetype)
		allFiles.extend(files)

	return allFiles


#===================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("root", metavar="directory", help="Root folder where the videos are stored")
	parser.add_argument("w", metavar="width", type=int, help="Number of video columns to use")
	parser.add_argument("h", metavar="height", type=int, help="Number of video rows to use")
	args = parser.parse_args()
	return args


#===================================================================================================
if (__name__ == "__main__"):
	args = parse_args()
	files = get_files(*args._get_kwargs())
	app = QtWidgets.QApplication([])
	app.setApplicationName("Video Wall")
	window = MainWindow(files, (args.w, args.h))

	timer = QtCore.QTimer()
	timer.timeout.connect(lambda: None)
	timer.start(100)

	sys.exit(app.exec_())
