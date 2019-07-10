#!/bin/bash


################################################################################
#    PRINTING HELPER METHODS                                                   #
################################################################################

func_call=1

print_line()
{
    local OPTIND OPTION OPTARG num_char

    num_char=$(tput cols)

    while getopts 'n:' OPTION
    do
        case $OPTION in
            n)  num_char="${OPTARG}";;
            *)  printf 'print_line got unsupported option: %s' "${OPTION}";;
        esac
    done

    shift $(( OPTIND - 1 ))

    for ((i=1; i<=$num_char; i++))
    do
        echo -n $1
    done
    echo
}


function print_message(){

    LEADING_TAB='    '
    echo -e "\n${LEADING_TAB}TEST #$func_call    "
    print_line '-'
    
    if [[ $1 = 0 ]]
    then
        echo " PASSED: $2"
    else
        echo " FAILED: $2"
    fi

    echo
    print_line "="
    echo

    ((func_call++))

}

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


echo
print_line '#'
echo -e "\n        PEREGRINE TESTING\n"
print_line '#'
echo


#    TEST: LOADING MODULES
########################################

echo -e "Starting loading module test\n"

# get the first three modules to load
modules_str=( $(ls /software/modules/all -1 | head -3) )
modules_array=${modules_str[@]}

# load the first three modules
module load $modules_array

# check that all modules are loaded

# TODO: This grep is wrong
returned_num_modules_loaded=$(grep_loaded_modules -c $modules_array)
expected_num_modules_loaded=3
test $returned_num_modules_loaded -eq $expected_num_modules_loaded && print_message 0 "All modules loaded" || print_message 1 "All modules not loaded"


#    TEST: DELETING MODULES
########################################

echo -e "Starting deleting module test\n"

# delete the first module
module_str=${t_module_list[0]}
module del $module_str

# check that the module has been removed
is_deleted=$(grep_loaded_modules "$t_module")

test -z $is_deleted && print_message 0 "Module deleted successfully" || print_message 1 "Module failed to delete"


#    TEST: SAVING & PURGING MODULES
#######################################

echo -e "Starting purging module test\n"

# save the other two modules as the default list
module save &> /dev/null  # don't print output

# purge all modules
module purge

# check that all modules have been removed
loaded_modules=$(get_loaded_modules)
if [[ "$loaded_modules" = "No modules loaded" ]]
then
    print_message 0 "All modules purged"
else
    print_message 1 "All modules not purged"
fi


#    TEST: RESTORING MODULES
#########################################

echo -e "Starting restoring module test\n"

# restore from default list
module restore &> /dev/null

# check that the modules have been restored
returned_num_modules_loaded=$(grep_loaded_modules -c $t_module_array)
expected_num_modules_loaded=2
#test $returned_num_modules_loaded -eq $expected_num_modules_loaded && echo "All modules restored" || echo "All modules not restored"
test $returned_num_modules_loaded -eq $expected_num_modules_loaded && print_message 0 "All modules restored" || print_message 1 "All modules not restored"



################################################################################
#    I/O TESTS                                                                 #
################################################################################

echo -e "Checking for write access to /home\n"

# check if you can write to /home
#
# NOTE: this does not actually write anything, as there is a tape backup for /home.
#   You only check for *permission* to write.
test -w /home && print_message 0 "/home is writeable" || print_message 1 "/home is not writeable"

echo -e "Checking for write access to /data\n"

# check if you can write to /data
test -w /data && print_message 0 "/data is writeable" || print_message 1 "/data is not writeable"



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
fi

echo -e "Running test job\n"

sbatch_output="$(sbatch peregrine_test_job.sh)"
job_id="$(echo $sbatch_output | grep -oE '[^ ]+$')"

echo "Test JobID: $job_id"

scontrol_output="$(scontrol show jobid -dd $job_id)"

# check that the job is submitted
test -n "$(echo $scontrol_output | grep -E 'PENDING|RUNNING|COMPLETED')" && print_message 0 "Test job successfully submitted" || print_message 1 "Test job failed to submit"

#    TEST: CANCEL A JOB
########################################

echo -e "Cancelling test job"

# cancel the job
scancel $job_id

scontrol_output="$(scontrol show jobid -dd $job_id)"

# check that the job is cancelled
test -n "$(echo $scontrol_output | grep 'CANCELLED')" && print_message 0 "Test job successfully cancelled" || print_message 1 "Test job failed to cancel"


