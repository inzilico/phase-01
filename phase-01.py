"""
	Phasing NGS and array datasets with shapeit or eagle.
	Author: Gennady Khvorykh, info@inzilico.com
	Only autosomes are phased. They are processed in parallel.
	The input is vcf.gz file. The reference panel and recombination map are applied.
	The genomic assembly is GRCh38.
	Date created: January 23, 2024
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
		run(cmd, shell = True)
	
def phase_shapeit(i):
	"""
		Phase a chromosome with SHAPEIT tool
	"""
	print("Processing chromosome", i)
	map_file = f"{res['map38']}/plink.chr{i}.GRCh38.map.shapeit.txt"
	ref_file = f"{res['ref1kg38']}/chr{i}.vcf.gz"
	phased_file = f"chr{i}.phased.bcf"
	cmd = f"{res['shapeit']} --input {input_file} --region chr{i} --reference {ref_file} \
		--map {map_file} --thread {cpu} --output {phased_file} --log chr{i}.log"
	p = run(cmd, shell = True)
	if p.returncode != 0:
		raise Exception(f'Phase chromosome {i} invalid result: {p.returncode}')
	check_file(phased_file)


def phase_eagle(i):
	"""
		Phase a chromosome with Eagle tool
	"""
	print("Processing chromosome", i)
	map_file = f"{res['eagle']}/tables/genetic_map_hg38_withX.txt.gz"
	output_prefix = f"chr{i}"	
	ref_file = f"{res['ref1kg38']}/{output_prefix}.vcf.gz"
	cmd = f"{res['eagle']}/eagle --vcfRef={ref_file} \
		--geneticMapFile={map_file} --chrom={i} \
		--vcfOutFormat=u --outPrefix={output_prefix}.phased \
		--vcfTarget={input_file}"
	p = run(cmd, shell=True, capture_output=True, text=True)
	print(p.stdout, file=open(f'{output_prefix}.log', 'w'))
	print("\n", p.stderr, file=open(f'{output_prefix}.log', 'a'))

# === End of Functions ===

# Parse command line arguments
parser = argparse.ArgumentParser(description="A wrapper script to phase genotypes")
parser.add_argument(
    "vcfgz_file", help="path/to/filename.vcf.gz with testing genetic variants"
)
parser.add_argument(
    "-r", "--res_file", required=True, help="path/to/file.csv with paths to tools"
)
parser.add_argument("-c", "--cpu", default=22, help="The number of CPUs (default: 20)")
parser.add_argument("-t", "--tool", default="shapeit", help="The tool to phase the genotypes: shapeit, eagle (default: shapeit)")
args = parser.parse_args()

# Initiate variables
vcfgz_file = args.vcfgz_file
res_file = args.res_file
tool = args.tool
cpu = args.cpu

# Check input
check_file(vcfgz_file)

# Load resources
res = load_resources(res_file)

# Get time
t1 = time.time()

# Copy input file into working folder
input_file = vcfgz_file
output_file = os.path.basename(input_file)
if not os.path.isfile(output_file):
	cmd = f"rsync -avzh {input_file} {output_file}"
	print(cmd)
	run(cmd, shell = True)
check_file(output_file)

# Index input file 
index(output_file)

# Process further the copy of input file in the working folder
input_file = output_file

# Loop over the chromosomes and phase them
if tool == "shapeit":
	with Pool(cpu) as pool:
		pool.map(phase_shapeit, range(1, 23))
elif tool == "eagle":
	with Pool(cpu) as pool:
		pool.map(phase_eagle, range(1, 23))
#	for i in range(22, 23):
#		phase_eagle(i)
else:
	print("Unknown tool:", tool)
	sys.exit(1)

# Glob phased files
bcfs = glob.glob("*.phased.bcf")

# Sort phased files
bcfs.sort()

# Concatenate phased bcf files
bcf_arg = ' '.join(bcfs) 
output_file = input_file.replace(".vcf.gz", ".phased.vcf.gz")
cmd = f"{res['bcftools']} concat --write-index --threads {cpu} -Oz -o {output_file} {bcf_arg}"
p = run(cmd, shell = True)
if p.returncode != 0:
	raise Exception(f'Concatenate bcf failed: {p.returncode}')

# Glob log files
logs = glob.glob("chr*.log")
logs.sort()

# Concatenate log files
log_arg = ' '.join(logs)
log_file = input_file.replace(".vcf.gz", ".log")
cmd = f"cat {log_arg} > {log_file}"
p = run(cmd, shell = True)
if p.returncode != 0:
	raise Exception(f'Concatenate log failed: {p.returncode}')

# Clean
for bcf in bcfs:
	os.remove(bcf)

for log in logs:
	os.remove(log)

# Show time elapsed
dur = time.time()-t1
dur = time.strftime("%H:%M:%S", time.gmtime(dur))
print("\nTime spent: ", dur, file = open(log_file, 'a'))
