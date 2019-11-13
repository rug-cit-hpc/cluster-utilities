#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    
    // create the MPI environment
    MPI_Init(&argc, &argv);

    // get rank of the processor
    int MPI_world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &MPI_world_rank);
    
    // get the number of processors
    int MPI_world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &MPI_world_size);

    printf("Hello world (rank=%d, size=%d)\n", MPI_world_rank, MPI_world_size);

    MPI_Finalize();
} 
