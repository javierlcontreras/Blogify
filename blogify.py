from command_line_parser import CommandLineParser
from compiler import Compiler
from paths import PATHS

def main():
	program_path, command_line_options = CommandLineParser().parseCommandLineOptions()

	input_path = command_line_options.input_path
	output_path = command_line_options.output_path
	cname = command_line_options.cname

	boilerplate_path = "/".join(program_path.split("/")[:-1]) + "/boilerplate"
	
	compiler = Compiler(input_path, output_path, boilerplate_path, cname)
	compiler.compile()


if __name__ == "__main__":
	main()