#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p16(int32_t x, int32_t y) {
    int32_t o1 = x ^ y;
    int32_t o2 = -((uint32_t) x >= (uint32_t) y);
    int32_t o3 = o1 & o2;
    return o3 ^ y;
  }
}

int main() {
  srand(98274);
  for (int i = 0; i < 15; ++i) {
    printf("%d\n", p16(i, i));
    printf("%d\n", p16(i, i-1));
  }
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p16(rand(),rand()));
  }


  return 0;
}
