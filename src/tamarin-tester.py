from shared import *
from bench import *
from test import *
import argparse
import pathtype
import os
from blessings import Terminal
from settings import Settings

term = Terminal()

des = "This program can be used to generate benchmark files for Tamarin which record correct results for a directory of protocols. Then it can be used to test an altered Tamarin compilation for correctness by comparing against these results. First navigate to a directory containing finished protocols and run Tamarin-Tester GOOD_TAMARIN_PATH. Then run Tamarin-Tester DEV_TAMARIN_PATH --b benchmark.txt and inspect the results."


#TODO Make some of these exclusive / grouped!
parser = argparse.ArgumentParser(description=des)
parser.add_argument("-p","--protocols", metavar='DIR', help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd())
parser.add_argument("-b","--benchmark", metavar='FILE', help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("tamarin", metavar='FILE', help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("-c","--contingency", metavar='2', help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("-r","--repetitions", metavar='3', help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
parser.add_argument("-mp","--maxproof", metavar='INT',help="Maximum time to run a proof for",type=float)
parser.add_argument("-f","--flags", metavar='FLAGS',help="User defined flags to pass to Tamarin for EVERY protocol",type=str)
parser.add_argument("-o","--output", metavar='benchmark.txt',help="Location of output file, defaults to local directory",type=pathtype.PathType(exists=False, type='file'))
parser.add_argument("-mc","--maxcheck", metavar='INT', help="Maximum time to run well-formedness check for",type=float)
parser.add_argument("-v","--verbose",help="Enabled verbose logging",action='store_true')
parser.add_argument("-over", "--overtime", help="Filter out protocols which are expected to timeout",action='store_true')


args = parser.parse_args()

if args.benchmark is None and (args.maxproof is None or args.maxcheck is None):
				print(term.bold(term.red("ERROR ")) + "In benchmark mode you MUST specify how long to attempt checks and proofs for!")
				exit(1)
				
config = Settings(args)

print(term.bold(term.blue("INFORMATIONAL ")) + "Tamarin Tester v0.3")
if config.verbose:
	print(term.bold(term.blue("INFORMATIONAL ")) + "Verbose Logging Enabled")

if args.benchmark is None:
	print(term.bold(term.blue("INFORMATIONAL ")) + "Mode: Create Benchmark")
	if config.verbose:
		print(term.bold(term.blue("INFORMATIONAL ")) + "Running Tamarin Executable: " + config.tamarin)	
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Output Location: " + config.output)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmarking Protocols in: " + config.protocols)
		print(term.bold(term.blue("INFORMATIONAL ")) + "User flags: " + config.userFlags)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Repetitions: " + str(config.repetitions))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Check Time: " + str(config.checkTime))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Proof Time: " + str(config.absolute))
	b = Bencher(config)
	b.estBenchTime()
	b.performBenchmark()
else:
	print(term.bold(term.blue("INFORMATIONAL ")) + "Mode: Comparing to Benchmark")
	if config.verbose:
		print(term.bold(term.blue("INFORMATIONAL ")) + "Testing Tamarin Executable: " + config.tamarin)	
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Input Location: " + str(config.benchmark.name))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Testing Protocols in: " + config.protocols)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Contingency Factor: " + str(config.contingency))
		print(term.bold(term.blue("INFORMATIONAL ")) + "User flags: " + config.userFlags)
	t = Tester(config)
	if t.checkOvertime() and config.removeOvertime:
			t.filterOvertime()
	t.estTestTime()
	t.performTest()
