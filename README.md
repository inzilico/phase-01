# Phasing of NGS data

The repository has some scripts to automate the phasing with the use of referemce panels. 

## Tools

* `SHAPEIT5` is a software package to estimate haplotypes in large genotype datasets (WGS and SNP array). [website](https://odelaneau.github.io/shapeit5/)

* `Eagle2` is a very fast HMM-based algorithm to estimate haplotypes within a genotyped cohort or using a phased reference panel. [manual](https://alkesgroup.broadinstitute.org/Eagle/#x1-20001)

## Scripts

* `phase-01.py` is a wrapper script to phase the genotypes given as vcf.gz file by SHAPEIT or Eagle tools.  

## Usage

```bash
# Phase with SHAPEIT


# Phase with Eagle


```
## Third-party datasets

### Reference haplotypes


### Recombination map