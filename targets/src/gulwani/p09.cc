#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p09(int32_t x) {
    int32_t o1 = x >> 31;
    int32_t o2 = x ^ o1;
    return o2 - o1;
  }
}

int main() {
  srand(6329543);
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p09(rand() & 0x7FFFFFFF));
  }
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p09(rand() | 0x80000000));
  }

  return 0;
}
