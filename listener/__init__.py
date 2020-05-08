import sys,os,argparse,logging
import keyboard
import listener.output as output
import listener.config as config
from listener.keyboard import Listener
from listener.ui import view 

def run_cli(args):
	try:
		cfg = config.parse_yaml(args.config)
		Listener(cfg[args.format], args.output).listen()
	except config.ConfigError as err:
		logging.error("Failed to load config, exitting.")

def run_gui(args):
	view.init_ui()	

def output_handler(path):
	logging.info("Writing to file: %s", path)
	return output.FileOutput(path) 
	
def main():
	default_bindings_path = os.path.join('default_bindings.yml')

	parser = argparse.ArgumentParser(description="Use keyboard shortcuts to maintain the global state counters in Magic: the Gathering")
	
	subparsers = parser.add_subparsers(dest='command', help="help for commands")
	subparsers.required = True

	cmdline = subparsers.add_parser("cli", help="Run in a console, with specified parameters")

	cmdline.add_argument('-f', '--format', metavar='FMT', default='edh', help='selects the format of the game')
	cmdline.add_argument('-o', '--output', metavar='PATH', action='append', default=[output.StdOutOutput()], help='file to write the game state to (e.g. for OBS)', type=output_handler)
	cmdline.add_argument('-c', '--config', metavar='PATH', default=default_bindings_path, help='path to the yaml config file')
	cmdline.set_defaults(func=run_cli)
	
	gui = subparsers.add_parser("gui", help="Run in a GUI")
	gui.set_defaults(func=run_gui)

	args = parser.parse_args()
	args.func(args)
