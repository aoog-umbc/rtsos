#!/bin/bash
#SBATCH --job-name=run_luts     # create a short name for your job
#SBATCH --output=slurm-%A.%a.out # stdout file
#SBATCH --error=slurm-%A.%a.err  # stderr file
#SBATCH --nodes=1                # node count
#SBATCH --ntasks-per-node=1
###SBATCH --ntasks=5               # total number of tasks across all nodes
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=64G         # memory per cpu-core (4G is default)
##SBATCH --time=100:30:00          # total run time limit (HH:MM:SS)
#SBATCH --exclude=poseidon-compute-[1-2,13]
#SBATCH --requeue       # this will make sure if a node fails, it will be requeued again
#SBATCH --array=[0-829]              # job array with index values 0, 1, 2, 3, 4
export TMPDIR=/dev/shm
##sleep 1
echo "My SLURM_ARRAY_JOB_ID is $SLURM_ARRAY_JOB_ID."
echo "My SLURM_ARRAY_TASK_ID is $SLURM_ARRAY_TASK_ID"
echo "Executing on the machine:" $(hostname)

##echo -n " Instrument number: "
##read $instrument
##echo $instrument
python run_luts.py ###$instrument

