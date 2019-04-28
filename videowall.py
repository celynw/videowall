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
	def __init__(self, widgetParent, mouseDoubleClickEvent, path):
		self.videoFrame = QtWidgets.QFrame()
		widgetParent.addWidget(self.videoFrame)
		self.videoFrame.mouseDoubleClickEvent = mouseDoubleClickEvent
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
	#-----------------------------------------------------------------------------------------------
	def __init__(self, files, size, *args, **kwargs):
		super().__init__(*args, **kwargs)
		shuffle(files)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.move(0, 0)
		self.resize(1920, 1080)
		self.show()
		self.mainFrame = QtWidgets.QFrame()
		self.setCentralWidget(self.mainFrame)
		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)

		file = 0
		for row in range(size[1]):
			layoutRow = QtWidgets.QHBoxLayout()
			layoutRow.setContentsMargins(0, 0, 0, 0)
			for col in range(size[0]):
				file += 1
				if (file < len(files)):
					Frame(layoutRow, self.mouseDoubleClickEvent, files[file])
			layout.addLayout(layoutRow)
		self.mainFrame.setLayout(layout)
		self.show()

	#-----------------------------------------------------------------------------------------------
	def mouseDoubleClickEvent(self, event):
		if event.button() == Qt.LeftButton:
			if self.windowState() == Qt.WindowNoState:
				self.videoFrame1.hide()
				self.videoFrame.show()
				self.setWindowState(Qt.WindowFullScreen)
			else:
				self.videoFrame1.show()
				self.setWindowState(Qt.WindowNoState)

	#-----------------------------------------------------------------------------------------------
	def mouseDoubleClickEvent1(self, event):
		if event.button() == Qt.LeftButton:
			if self.windowState() == Qt.WindowNoState:
				self.videoFrame.hide()
				self.videoFrame1.show()
				self.setWindowState(Qt.WindowFullScreen)
			else:
				self.videoFrame.show()
				self.setWindowState(Qt.WindowNoState)


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
