#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p13(int32_t x) {
    int32_t o1 = x >> 31;
    int32_t o2 = -x;
    int32_t o3 = o2 >> 31;
    return o1 | o3;
  }
}

int main() {
  srand(32654234);
  for (int i = -10; i < 10; ++i) {
    printf("%d\n", p13(i));
  }
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p13(rand() & 0x7FFFFFFF));
    printf("%d\n", p13(rand() | 0x80000000));
  }

  return 0;
}
