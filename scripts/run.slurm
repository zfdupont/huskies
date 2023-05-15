#!/bin/bash

#SBATCH --job-name=huskies10k
#SBATCH --output=res.txt
#SBATCH --time=48:00:00

#SBATCH --nodes=4
#SBATCH --cpus-per-task=20
#SBATCH --ntasks-per-node=3
#SBATCH --spread-job

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=zachary.dupont@stonybrook.edu

module load slurm
module load mpi4py/3.0.3
module load mvapich2/gcc/64/2.2rc1
module load gnu-parallel

pip install -r requirements.txt

export DATABASE_URI="mongodb+srv://admin:admin@huskies.fwdwss9.mongodb.net/?retryWrites=true&w=majority"
export HUSKIES_HOME="/gpfs/home/zdupont"
export BATCH_SIZE=200
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
mkdir -p $HUSKIES_HOME/profiles


srun="srun -N1 --exclusive -vv"
# -N1                   queues 1 node for the job
# --exclusive           makes sure each node isnt being used by another job 

parallel="parallel -N 1 --delay .2 -j $SLURM_NTASKS --joblog parallel_joblog --resume"
# -N 1                  number of arguments to pass to each job
# --resume              will rerun any task that fails
# -j $SLURM_NTASKS      number of concurrent tasks at any given time


python preprocess_all.py
$parallel "$srun python -m cProfile -o $HUSKIES_HOME/profiles/generate.prof generate_plans.py arg1:{1}" ::: {1..100}
python -m cProfile -o $HUSKIES_HOME/profiles/analysis.prof ensemble_analysis.py
python fill_database.py -c huskies 