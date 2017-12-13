#!/usr/bin/env python3.5

# External Imports
from argparse import ArgumentParser, FileType
from pathtype import PathType
import os
import sys
import textwrap

# Internal Imports
from shared import DESCRIPTION, VERSION, INFORMATIONAL, ERROR, Settings
from test import Tester
from bench import Bencher

parser = ArgumentParser(description=DESCRIPTION, add_help=False)

mandatory = parser.add_argument_group(
    'Mandatory Arguments', 'This argument is mandatory in BOTH modes')
tamarin_help = "Path to the tamarin binary you wish to test/benchmark"
mandatory.add_argument("tamarin", metavar='TAMARIN_BINARY',
                       help=tamarin_help, type=FileType('r'))

globals = parser.add_argument_group(
    'Optional Arguments', 'These arguments can be passed to both modes')

protocols_help = textwrap.dedent("""\
The directory containing the protocols you wish to test/benchmark. The
directory will be scanned recursively for all .spthy files. The default is to
take the current working directory""".replace('\n', ''))
globals.add_argument("-p", "--protocols", metavar='PROTOCOL_DIR',
                     help=protocols_help, type=PathType(exists=True, type='dir'), default=os.getcwd())

flags_help = textwrap.dedent("""\
User defined flags to pass to the tamarin binary, EVERY time it is invoked. See
the README for how to set flags on a per-protocol basis""".replace('\n', ''))

globals.add_argument("--flags", metavar='FLAGS', help=flags_help, type=str)

globals.add_argument("-v", "--verbose", action='store_true',
                     help='Run in verbose mode')

globals.add_argument('--version', action='version',
                     version=VERSION, help='Print version information and exit')

globals.add_argument('-h', '--help', action='help',
                     help='Print this help message')


test = parser.add_argument_group(
    'TEST Mode', 'This mode is selected by default')

input_help = textwrap.dedent("""\
By default tamarin-tester will look for a file named 'benchmark.res' located in
the top level protocol directory. This option allows you to select a different
file.""".replace('\n', ''))
test.add_argument("-i", "--input", metavar='BENCHMARK_FILE',
                  help=input_help, type=PathType(exists=True, type='file'))

contingency_help = textwrap.dedent("""\
When running a test for a protocol file. tamarin-tester will wait for the
expected running time (in seconds) X the contingency factor. This is by default
2, but if you have benchmark file from a faster machine than this machine, you
may need to raise it.""".replace('\n', ''))
test.add_argument("--contingency", metavar='2',
                  help=contingency_help, type=int, default=2)

overtime_help = textwrap.dedent("""\
This option is only applied if you also specify a max proof time and if passed
will tell tamarin-tester to not test any protocols with an expected running
time greater than the max proof time. These protocols will be reported as
OVERTIME in the statistics rather than FAILED""".replace('\n', ''))
test.add_argument("--overtime", help=overtime_help, action='store_true')

failfast_help = textwrap.dedent("""\
If passed, the program will quit upon a failing test with return code 1""".replace('\n', ''))
test.add_argument(
    "--failfast", help=failfast_help, action='store_true')

bench = parser.add_argument_group(
    'BENCHMARK Mode', 'this mode is selected by passing --benchmark')

benchmark_help = textwrap.dedent("""\
This flag tells tamarin-tester to run in benchmark mode. Consequently it is
mandatory to pass -mc and -mp flags detailed in the Timeout Arguments section
below""".replace('\n', ''))
bench.add_argument("--benchmark", help=benchmark_help, action='store_true')

output_help = textwrap.dedent("""\
This is the location to write the benchmark file to after completion. By
default it will be written to the top level of the protocols directory, named
'benchmark.res'""".replace('\n', ''))
bench.add_argument("-o", "--output", metavar='BENCHMARK_FILE',
                   help=output_help, type=PathType(exists=False, type='file'))

repetitions_help = textwrap.dedent("""\
When calculating the average running time of a protocol, this is the number of
samples to take. By default it is set to 1. If you need to benchmark on a
machine with an unstable workload, setting it high will produce more reliable
results at the cost of much greater execution time""".replace('\n', ''))
bench.add_argument(
    "--repetitions",
    metavar='1',
    help=repetitions_help,
    type=int,
    default=1)

times = parser.add_argument_group(
    'Timeout Arguments', 'These arguments are MANDATORY for BENCHMARK mode but OPTIONAL for TEST mode')
maxcheck_help = textwrap.dedent("""\
Maximum time (in seconds) to run well-formedness check for. In TEST Mode, this
is loaded from the file as the maximum running time of the protocols
benchmarked, that are also in the protocol directory.""".replace('\n', ''))
times.add_argument("-mc", "--maxcheck", metavar='FLOAT',
                   help=maxcheck_help, type=float)

maxproof_help = textwrap.dedent("""\
Maximum time (in seconds) to run a proof for. In TEST Mode, this is loaded from
the file as the maximum running time of the protocols benchmarked that are also
in the protocol directory X the contingency value which is described below.""".replace('\n', ''))
times.add_argument(
    "-mp",
    "--maxproof",
    metavar='FLOAT',
    help=maxproof_help,
    type=float)

args = parser.parse_args()

if args.benchmark and (args.maxproof is None or args.maxcheck is None):
    print(
        ERROR +
        "In benchmark mode you MUST specify how long to attempt checks and proofs for!")
    sys.exit(1)

config = Settings(args)

print(INFORMATIONAL + VERSION)
if config.verbose:
    print(INFORMATIONAL + "Verbose Logging Enabled")

if args.benchmark:
    print(INFORMATIONAL + "Mode: Create Benchmark")
    if args.output is not None:
        config.output = args.output
    else:
        config.output = config.protocols + "/benchmark.res"
        print(INFORMATIONAL + "Using default output location " + config.output)
    if os.path.isfile(config.output):
        print(ERROR + "file already exists at " + config.output)
        sys.exit(1)
    config.absolute = args.maxproof
    config.checkTime = args.maxcheck
    if config.verbose:
        print(INFORMATIONAL + "Running Tamarin Executable: " + config.tamarin)
        print(INFORMATIONAL + "Benchmark Output Location: " + config.output)
        print(INFORMATIONAL + "Benchmarking Protocols in: " + config.protocols)
        print(INFORMATIONAL + "User flags: " + config.userFlags)
        print(INFORMATIONAL +
              "Benchmark Repetitions: " +
              str(config.repetitions))
        print(INFORMATIONAL + "Max Check Time: " + str(config.checkTime))
        print(INFORMATIONAL + "Max Proof Time: " + str(config.absolute))
    b = Bencher(config)
    b.estBenchTime()
    b.performBenchmark()
else:
    if args.input is not None:
        config.input = args.input  # Where to read the benchmark file from
    else:
        config.input = config.protocols + "/benchmark.res"
        print(INFORMATIONAL + "Using default input location " + config.input)
    if not os.path.isfile(config.input):
        print(ERROR + "could not find benchmark file " + config.output)
        sys.exit(1)
    if args.maxproof is not None:
        config.absolute = args.maxproof
    if args.maxcheck is not None:
        config.checkTime = args.maxcheck
    print(INFORMATIONAL + "Mode: Testing")
    if config.verbose:
        print(INFORMATIONAL + "Testing Tamarin Executable: " + config.tamarin)
        print(INFORMATIONAL + "Benchmark Input Location: " + str(config.input))
        print(INFORMATIONAL + "Testing Protocols in: " + config.protocols)
        print(INFORMATIONAL + "Contingency Factor: " + str(config.contingency))
        print(INFORMATIONAL + "User flags: " + config.userFlags)
    t = Tester(config)
    if t.checkOvertime() and config.removeOvertime:
        t.filterOvertime()
    t.estTestTime()
    t.performTest()
