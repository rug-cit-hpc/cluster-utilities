#!/bin/bash


################################################################################
#    MODULE MANAGEMENT TESTS                                                   #
################################################################################

function get_loaded_modules(){
    # get a list of modules which are loaded in the current session

    loaded_modules=`(module -t list 2>&1)`  # -t option forces output to 1 column
    echo $loaded_modules
}

function grep_loaded_modules(){
    # grep the loaded modules list for the given argument
    # if the -c flag is given, count the number of matches

    loaded_modules=$(get_loaded_modules)

    while getopts "c" OPTION
    do
        case $OPTION in
            c)
		module_array=$1
		
                #    list modules        regex  (replace space with |)   count
		echo "$loaded_modules" | grep -E ${module_array//\ /|} | wc -l
                ;;
	    *)
                echo "$loaded_modules" | grep "$1"
		;;
	esac
    done
}


#    TEST: LOADING MODULES
########################################

# get the first three modules to load
modules_str=( $(ls /software/modules/all -1 | head -3) )
modules_array=${modules_str[@]}

# load the first three modules
module load $modules_array

# check that all modules are loaded
returned_num_modules_loaded=$(grep_loaded_modules -c $modules_array)
expected_num_modules_loaded=3
test $returned_num_modules_loaded -eq $expected_num_modules_loaded && echo "All modules loaded" || echo "All modules not loaded"


#    TEST: DELETING MODULES
########################################

# delete the first module
module_str=${t_module_list[0]}
module del $module_str

# check that the module has been removed
is_deleted=$(grep_loaded_modules "$t_module")
test -z $is_deleted && echo "Module deleted" || echo "Module not deleted"


#    TEST: SAVING, PURGING & RESTORING MODULES
########################################

# save the other two modules as the default list
module save &> /dev/null  # don't print output

# purge all modules
module purge

# check that all modules have been removed
loaded_modules=$(get_loaded_modules)
if [[ "$loaded_modules" = "No modules loaded" ]]
then
    echo "All modules purged"
else
    echo "All modules not purged"
fi

# restore from default list
module restore

# check that the modules have been restored
returned_num_modules_loaded=$(grep_loaded_modules -c $t_module_array)
expected_num_modules_loaded=2
test $returned_num_modules_loaded -eq $expected_num_modules_loaded && echo "All modules restored" || echo "All modules not restored"



################################################################################
#    I/O TESTS                                                                 #
################################################################################

# check if you can write to /home
#
# NOTE: this does not actually write anything, as there is a tape backup for /home.
#   You only check for *permission* to write.
test -w /home && echo '/home is writeable' || echo '/home is not writeable'

# check if you can write to /data
test -w /data && echo '/data is writeable' || echo '/data is not writeable'



################################################################################
#    JOB MANAGEMENT & MPI TESTS                                                #
################################################################################

#    TEST: SUBMIT A JOB
########################################

# ensure that the test file exists
if [ ! -x ./peregrine_test_job.sh ];
then
    echo "peregrine_test_job.sh not found or is not executable"
    echo "test_peregrine.sh cannot continue. Quitting."
    exit 126

job_id=`$(sbatch peregrine_test_job.sh)`

# check that the job is submitted
test -n `$(jobinfo $job_id)` && echo "Test job successfully submitted" || echo "Test job failed to submit"


#    TEST: CANCEL A JOB
########################################

# cancel the job
scancel $job_id

# check that the job is cancelled
test -z `(jobinfo $job_id)` && echo "Test job successfully cancelled" || echo "Test job failed to cancel"

# check that /scratch is cleared when job is cancelled
percent_used=`df /scratch | awk 'NR>1{print substr($5, 1, length($5)-1}'`  # get % used on /scratch (stripping the '%' sign)
percent_thresh=5  # 5% minimum usage

test $percent_used -le $percent_thresh && echo "/scratch space successfully emptied" || echo "/scratch space not cleared"

