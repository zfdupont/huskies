#!usrbinenv bash

#SBATCH --nodes=1
#SBATCH --time=30000
#SBATCH --partition=short-24core
#SBATCH --job-name=analysis_job

python ensemble_analysis.py