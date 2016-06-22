#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p22(int32_t x) {
    int32_t o1 = x >> 1;
    int32_t o2 = o1 ^ x;
    int32_t o3 = o2 >> 2;
    int32_t o4 = o2 ^ o3;
    int32_t o5 = o4 & 0x11111111;
    int32_t o6 = o5 * 0x11111111;
    int32_t o7 = o6 >> 28;
    return o7 & 0x1;
  }
}

int main() {
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p22(i));
  }
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p22(rand()));
  }

  return 0;
}
