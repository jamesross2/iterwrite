"""A program that prints bad output in a loop."""

import argparse
import random

import iterwrite

parser = argparse.ArgumentParser("A model with messy printing output")
parser.add_argument("--iter_count", help="Number of iterations to perform.", default=100, type=int)
parser.add_argument("--iterwrite", help="If set, uses the iterwrite package to print results", action="store_true")
ARGUMENTS = vars(parser.parse_args())

# repeatable
random.seed(672229)  # Twitter@_primes_

# newlines and spaces act as margin to make cropping easier
print("\n  Running some code with {} printing within a loop.\n".format("clean" if ARGUMENTS["iterwrite"] else "messy"))

# set up loop (very artificial)
running_value = 1.0
if ARGUMENTS["iterwrite"]:
    writer = iterwrite.Iterwriter(iter="    Iteration: {:d}", value="value: {:f}", delta="delta: {:f}")
else:
    writer = "    Iteration: {iter}, value: {value}, delta: {delta}"

# make some messy output
for iter in range(ARGUMENTS["iter_count"]):
    delta = round(random.normalvariate(0, iter), random.randint(1, 12))
    running_value = round(running_value + delta, random.randint(1, 12))
    if (iter % 10) == 0:
        print(writer.format(iter=iter + 1, value=running_value, delta=delta))

# margin
print("\n")
