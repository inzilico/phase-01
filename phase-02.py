"""
	Phasing NGS and array datasets with Beagle.
	Author: Gennady Khvorykh, info@inzilico.com
	Only autosomes are phased. They are processed in parallel.
	The input is vcf.gz file. The reference panel and recombination map are applied.
	The genomic assembly is GRCh38.
	Date created: January 28, 2024
"""
import os, sys
from subprocess import run
import argparse
from multiprocessing import Pool
import glob
import time

# === Functions ===


def check_file(x):
    if not os.path.isfile(x):
        print(x, "doesn't exist")
        sys.exit(1)


def load_resources(res_file):
    res = {}
    with open(res_file, "r") as f:
        for line in f:
            values = line.strip().split(",")
            res[values[0]] = values[1]
    return res


def index(x):
    if not os.path.isfile(x + ".csi"):
        cmd = f"{res['bcftools']} index --threads {cpu} {x}"
        p = run(cmd, shell=True)
        if p.returncode != 0:
            raise Exception(f"Index {x} invalid result: {p.returncode}")


def phase_beagle(i):
    cmd = f"java -jar {res['beagle']} gt={vcfgz_file} \
        ref={res['ref1kg38']}/chr{i}.vcf.gz \
        map={res['plink_map']}/chr{i}.map \
        chrom=chr{i} out=chr{i}.phased impute=false nthreads=1"
    p = run(cmd, shell=True)
    if p.returncode != 0:
        raise Exception(f"Phase chromosome {i} invalid result: {p.returncode}")
    phased_file = f"chr{i}.phased.vcf.gz"
    check_file(phased_file)
    index(phased_file)


# === End of Functions ===

# Parse command line arguments
parser = argparse.ArgumentParser(description="A wrapper script to phase genotypes")
parser.add_argument(
    "vcfgz_file", help="path/to/filename.vcf.gz with testing genetic variants"
)
parser.add_argument(
    "-r", "--res_file", required=True, help="path/to/file.csv with paths to tools"
)
parser.add_argument("-c", "--cpu", default=22, help="The number of CPUs (default: 22)")
parser.add_argument(
    "-t",
    "--tool",
    default="beagle",
    help="The tool to phase the genotypes: beagle (default: beagle)",
)
args = parser.parse_args()

# Initiate variables
vcfgz_file = args.vcfgz_file
res_file = args.res_file
tool = args.tool
cpu = args.cpu

# Check file
check_file(vcfgz_file)

# Load resources
res = load_resources(res_file)

# Get time
t1 = time.time()

# Loop over the chromosomes and phase them
if tool == "beagle":
    with Pool(cpu) as pool:
        pool.map(phase_beagle, range(1, 23))
else:
    print("Unknown tool:", tool)
    sys.exit(1)

# Glob phased files
vcfs = glob.glob("*.phased.vcf.gz")

# Sort phased files
vcfs.sort()

# Concatenate phased vcf files
vcf_arg = " ".join(vcfs)
prefix = os.path.basename(vcfgz_file).replace(".vcf.gz", "")
output_file = prefix + ".phased.vcf.gz"
cmd = f"{res['bcftools']} concat --write-index --threads {cpu} -Oz -o {output_file} {vcf_arg}"
p = run(cmd, shell=True)
if p.returncode != 0:
    raise Exception(f"Concatenate vcf failed: {p.returncode}")

# Glob log files
logs = glob.glob("chr*.phased.log")
logs.sort()

# Concatenate log files
log_arg = " ".join(logs)
log_file = prefix + ".log"
cmd = f"cat {log_arg} > {log_file}"
p = run(cmd, shell=True)
if p.returncode != 0:
    raise Exception(f"Concatenate log failed: {p.returncode}")

# Clean
for vcf in vcfs:
    os.remove(vcf)
    os.remove(vcf + ".csi")

for log in logs:
    os.remove(log)

# Show time elapsed
dur = time.time() - t1
dur = time.strftime("%H:%M:%S", time.gmtime(dur))
print("\nTime spent: ", dur, file=open(log_file, "a"))
