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
def main(*args):
	args = dict(args)
	root = Path(args["root"])
	if not root.exists():
		print("Directory '{}' not found".format(root))
		return


#===================================================================================================
if (__name__=="__main__"):
	args = parse_args()
	main(*args._get_kwargs())
