#include <stdio.h>
#include <omp.h>

int main() {

  int total = 0;

  #pragma omp parallel num_threads(7) // Use 7 threads
  {
    printf("Hello World!\n");     
    total = omp_get_num_threads();
  }

  printf("TOTAL THREADS: %d\n\n", total);

  return 0;
}
