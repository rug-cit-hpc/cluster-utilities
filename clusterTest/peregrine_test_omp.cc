#include <stdio.h>
#include <omp.h>

int main() {
  
  int total = omp_get_num_threads();
  printf("Starting %d processes...", total);
  
  #pragma omp parallel num_threads(7) // Use 7 threads
  {
    printf("Hello World!\n");     
  }

  return 0;
}
