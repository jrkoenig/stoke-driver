
#include <cstdlib>
#include <cstdio>
#include <cstdint>

extern "C" {
  size_t count_zero(uint8_t* a, size_t n) {
    size_t count = 0;
    for(size_t i = 0; i < n; i++) {
      count += (a[i] == 0);
    }
    return count;
  }
}

int main() {
  srand(169846834);
  uint8_t* arr = new uint8_t[100];
  
  arr[0] = 0;
  printf("%zu", count_zero(arr, 1));
  arr[0] = 34;
  printf("%zu", count_zero(arr, 1));
  arr[0] = 1;
  printf("%zu", count_zero(arr, 1));
  arr[0] = 255;
  printf("%zu", count_zero(arr, 1));
  
  
  arr[0] = 0; arr[1] = 0;
  printf("%zu", count_zero(arr, 2));
  arr[0] = 0; arr[1] = 3;
  printf("%zu", count_zero(arr, 2));
  arr[0] = 87; arr[1] = 23;
  printf("%zu", count_zero(arr, 2));
  arr[0] = 0; arr[1] = 251;
  printf("%zu", count_zero(arr, 2));
  
  for(int i = 3; i < 30; i+=4) {
    for(int j = 0; j < 100; j++)
      arr[j] = rand() % i < 2 ? 0 : rand();
    
    printf("%zu", count_zero(arr, i));
    
    for(int j = 0; j < 100; j++)
      arr[j] = rand() % 2 == 1 ? 0 : rand();
    
    printf("%zu", count_zero(arr, i));
  }
  return 0;
}
