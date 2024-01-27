"""
    Estimate the switch error with vcftools.
    The input file is space delimited 3 column table, each row having 
    the path to first and second vcf.gz files and the sample id.
"""

import sys
from subprocess import run
from multiprocessing import Pool

def load_resources(res_file):
    res = {}
    with open(res_file, "r") as f:
        for line in f:
            values = line.strip().split(",")
            res[values[0]] = values[1]
    return res

def estimate_switch_error(arg):
    vcfgz1 = arg[0]
    vcfgz2 = arg[1]
    sample = arg[2]
    # Estimate 
    cmd = f"{res['vcftools']} --gzvcf {vcfgz1} --gzdiff {vcfgz2} --diff-switch-error --out {out_folder}/{sample}"
    run(cmd, shell = True)

# Initiat variables
res_file = 'res.csv'
input_file = sys.argv[1]
out_folder = sys.argv[2]
cpu = 20

# Load resources
res = load_resources(res_file)

# Load list of files to compare
args = []
with open(input_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        arg = line.strip().split(" ")
        args.append(arg)

# Estimate switch error
with Pool(cpu) as pool:
    pool.map(estimate_switch_error, args)

