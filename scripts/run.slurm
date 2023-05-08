#!/bin/bash
#
#SBATCH --job-name=huskies1k
#SBATCH --output=res.txt
#SBATCH --nodes=4
#SBATCH --time=48:00:00
#SBATCH --cpus-per-task=24
#SBATCH -p long-24core
#SBATCH --spread-job
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=zachary.dupont@stonybrook.edu

module load slurm
module load mpi4py/3.0.3
module load mvapich2/gcc/64/2.2rc1

pip install -r requirements.txt

export DATABASE_URI="mongodb+srv://admin:admin@huskies.fwdwss9.mongodb.net/?retryWrites=true&w=majority"
export HUSKIES_HOME="/gpfs/home/zdupont"
export TOTAL_PLANS=200
export RECOM_STEPS=1000


mkdir -p $HUSKIES_HOME/generated/GA/assignments
mkdir -p $HUSKIES_HOME/generated/GA/preprocess
mkdir -p $HUSKIES_HOME/generated/GA/ensemble
mkdir -p $HUSKIES_HOME/generated/GA/interesting
mkdir -p $HUSKIES_HOME/generated/NY/assignments
mkdir -p $HUSKIES_HOME/generated/NY/preprocess
mkdir -p $HUSKIES_HOME/generated/NY/ensemble
mkdir -p $HUSKIES_HOME/generated/NY/interesting
mkdir -p $HUSKIES_HOME/generated/IL/assignments
mkdir -p $HUSKIES_HOME/generated/IL/preprocess
mkdir -p $HUSKIES_HOME/generated/IL/ensemble
mkdir -p $HUSKIES_HOME/generated/IL/interesting

srun -c 24 -n 2 -N 2 python -m cProfile -o $HUSKIES_HOME/profiles/generate.prof generate_plans.py
python -m cProfile -o $HUSKIES_HOME/profiles/analysis.prof ensemble_analysis.py
python enacted_analysis.py
python fill_database.py