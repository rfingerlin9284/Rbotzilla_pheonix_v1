#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

def main():

	parser = argparse.ArgumentParser(description="mbot CLI interface")
	# Add arguments and sub-commands here
	# For example: parser.add_argument('--example', help='Example argument')
	args = parser.parse_args()
	# Handle the parsed arguments and invoke the necessary functions from your classes

if __name__ == "__main__":
	main()
