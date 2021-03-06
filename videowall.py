#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from random import shuffle
import sys
import vlc

# ==================================================================================================
class Frame():
	# ----------------------------------------------------------------------------------------------
	def __init__(self, widgetParent, mousePressEvent, path):
		self.videoFrame = QtWidgets.QFrame()
		widgetParent.addWidget(self.videoFrame)
		# Cannot loop indefinitely (e.g. =-1)
		self.vlcInstance = vlc.Instance(['--video-on-top', "--input-repeat=65535"])
		self.videoPlayer = self.vlcInstance.media_player_new()
		self.videoPlayer.video_set_mouse_input(False)
		self.videoPlayer.video_set_key_input(False)
		# self.videoPlayer.audio_set_mute(True)
		if sys.platform.startswith('linux'): # Linux (X)
			self.videoPlayer.set_xwindow(self.videoFrame.winId())
		elif sys.platform == "win32": # Windows
			self.videoPlayer.set_hwnd(self.videoFrame.winId())
		elif sys.platform == "darwin": # OSX
			self.videoPlayer.set_nsobject(int(self.videoFrame.winId()))
		self.videoFrame.mousePressEvent = lambda event: mousePressEvent(event, self)
		self.videoFrame.wheelEvent = self.wheelEvent
		self.load(path)

	# ----------------------------------------------------------------------------------------------
	def load(self, path):
		self.videoPlayer.set_media(self.vlcInstance.media_new(str(path)))
		self.videoPlayer.play()

	# ----------------------------------------------------------------------------------------------
	def wheelEvent(self, event):
		pos = self.videoPlayer.get_position()
		scale = -0.0001
		newPos = pos + event.angleDelta().y() * scale
		self.videoPlayer.set_position(newPos) # Cannot seem to set precise flag (False)


# ==================================================================================================
class MainWindow(QtWidgets.QMainWindow):
	keyPressed = QtCore.pyqtSignal(int)
	paused = False
	# ----------------------------------------------------------------------------------------------
	def __init__(self, files, size, resolution, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.files = files
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		screenNum = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
		geometry = QtWidgets.QApplication.desktop().screenGeometry(screenNum)
		self.move(geometry.left(), geometry.top())
		self.resize(*resolution)
		self.show()
		mainFrame = QtWidgets.QFrame()
		self.setCentralWidget(mainFrame)
		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)

		self.frames = []
		# TODO merge duplicate code
		shuffle(self.files)
		file = 0
		for row in range(size[1]):
			layoutRow = QtWidgets.QHBoxLayout()
			layoutRow.setContentsMargins(0, 0, 0, 0)
			for col in range(size[0]):
				file += 1
				if file < len(self.files):
					self.frames.append(Frame(layoutRow, self.mousePressEvent, self.files[file]))
			layout.addLayout(layoutRow)
		mainFrame.setLayout(layout)
		self.keyPressed.connect(self.on_key)
		self.show()

	# ----------------------------------------------------------------------------------------------
	def keyPressEvent(self, event):
		super().keyPressEvent(event)
		self.keyPressed.emit(event.key())

	# ----------------------------------------------------------------------------------------------
	def mousePressEvent(self, event, player):
		if event.button() == QtCore.Qt.LeftButton:
			shuffle(self.files)
			player.load(self.files[0])

	# ----------------------------------------------------------------------------------------------
	def on_key(self, key):
		if key == QtCore.Qt.Key_Escape or key == QtCore.Qt.Key_Q:
			# FIX Alt-F4 closes final sub-window. Focus parent first
			# app.quit(0)
			QtCore.QCoreApplication.quit()
		elif key == QtCore.Qt.Key_Space:
			self.paused = not self.paused
			for frame in self.frames:
				frame.videoPlayer.set_pause(self.paused)
		elif key == QtCore.Qt.Key_R:
			self.reshuffle()
		else:
			print(f"Key pressed: {key}")

	# ----------------------------------------------------------------------------------------------
	def reshuffle(self):
		# TODO merge duplicate code
		shuffle(self.files)
		file = 0
		for frame in self.frames:
			file += 1
			if file < len(self.files):
				frame.load(self.files[file])


# ==================================================================================================
def get_files(args):
	print("Recursively finding files...")
	if not args.root.exists():
		print(f"Directory '{args.root}' not found")
		quit(1)

	filetypes = [
		"*.mp4",
		"*.webm",
		"*.mkv",
		# "**/*.flv", # Not working
		# "**/*.gif", # Stills only
	]
	allFiles = []
	for filetype in filetypes:
		files = args.root.rglob(filetype)
		allFiles.extend(files)

	if len(allFiles) == 0:
		print(f"No compatible video files found in '{root}'")
		quit(1)
	print(f"Found {len(allFiles)} files")

	return allFiles


# ==================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("root", metavar="directory", help="Root folder where the videos are stored")
	parser.add_argument('w', metavar="width", type=int, help="Number of video columns to use")
	parser.add_argument('h', metavar="height", type=int, help="Number of video rows to use")
	parser.add_argument('ww', metavar="window width", type=int, nargs="?", default=1920, help="Window width")
	parser.add_argument('hh', metavar="window height", type=int, nargs="?", default=1080, help="Window height")
	args = parser.parse_args()
	args.root = Path(args.root)

	return args


# ==================================================================================================
if __name__ == "__main__":
	args = parse_args()
	files = get_files(args)
	app = QtWidgets.QApplication([])
	app.setApplicationName("Video Wall")
	window = MainWindow(files, (args.w, args.h), (args.ww, args.hh))

	sys.exit(app.exec_())
