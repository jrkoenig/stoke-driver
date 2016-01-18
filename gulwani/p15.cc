#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p15(int32_t x, int32_t y) {
    int32_t o1 = x | y;
    int32_t o2 = x ^ y;
    int32_t o3 = o2 >> 1;
    return o1 - o3;
  }
}

int main() {
  srand(439573);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p15(i, i));
    printf("%d\n", p15(i, i+1));
    printf("%d\n", p15(i, i-1));
  }
  for (int i = 0; i < 50; ++i) {
    printf("%d\n", p15(rand(),rand()));
  }


  return 0;
}
