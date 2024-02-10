import argparse
import sys
class CommandLineParser():
	
	def parseCommandLineOptions(self):
		parser = argparse.ArgumentParser(
			prog='Personal Web Builder',
			description='Given a folder structure, it builds a website',
			epilog='')

		parser.add_argument('-i', '--input', 
							dest='input_path',
	                    	help='Path of the blogify folder')
		parser.add_argument('-o', '--output', 
							dest='output_path',
							default='',
	                    	help='Path of the output website')
		parser.add_argument('-c', '--cname', 
						dest='cname',
						default='',
                    	help='CNAME of the website')
		args = parser.parse_args()
		if args.input_path[-1] == "/":
			args.input_path = args.input_path[:-1]
		if args.output_path == "":
			args.output_path = args.input_path + "_Blogify"

		return sys.argv[0], args