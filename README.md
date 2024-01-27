# Phasing of genotypes obtained by Next Generation Sequencing 

Phasing is the inference of haplotype phase from genotypes. The repository provides the scripts to automate the phasing with the use of several tools mentioned often in scientific literature.   

## Tools

* [SHAPEIT4](https://odelaneau.github.io/shapeit4/) is a software package to estimate haplotypes in large genotype datasets obtained by whole genome sequencing and DNA micoarrays (Delaneau et al., 2019).

* [Eagle2](https://alkesgroup.broadinstitute.org/Eagle/#x1-20001) is a very fast HMM-based algorithm to estimate haplotypes within a genotyped cohort or using a phased reference panel (Loh et al., 2016).

## Scripts

* `phase-01.py` is a wrapper script to phase the genotypes given as vcf.gz file by programs listed in Tools.  

```bash
# Phase with SHAPEIT
python3 /path/to/phase-01.py -r /path/to/resources.csv /path/to/sample.vcf.gz
```
where `resources.csv` is the comma seperated text file with the paths to the programs and files applied and `sample.vcf.gz` is the original genotypes under VCF file archived with `bgzip` tool.


```bash
# Phase with Eagle
python3 /path/to/phase-01.py -r /path/to/resources.csv --tool eagle /path/to/sample.vcf.gz
```

* `estimate-switch-error-01.py` is the script to estimate the switch error with vcftools for several samples.

```bash
python3 estimate-switch-error-01.py path/to/filename.txt path/to/out_folder
```

where `filename.txt` is the 3 column space delimited text file. Each row has the paths to first and second vcf.gz files as well as the sample id. 
`out_folder` is the folder to save the files created by `vcftools`.



## Third-party datasets

### Reference haplotypes


### Recombination map

## References

Olivier Delaneau, Jean-Francois Zagury, Matthew R Robinson, Jonathan Marchini, Emmanouil Dermitzakis. Accurate, scalable and integrative haplotype estimation. Nat. Comm. 2019.

Loh P-R, Danecek P, Palamara PF, Fuchsberger C, Reshef YA, Finucane HK, Schoenherr S, Forer L, McCarthy S, Abecasis GR, Durbin R, and Price AL. Reference-based phasing using the Haplotype Reference Consortium panel. Nature Genetics, 2016.

Loh P-R, Palamara PF, and Price AL. Fast and accurate long-range phasing in a UK Biobank cohort. Nature Genetics, 2016. 

