#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  uint32_t p24(uint32_t x) {
    x--;
    x |= x >> 1;
    x |= x >> 2;
    x |= x >> 4;
    x |= x >> 8;
    x |= x >> 16;
    x++;
    x += (x == 0);
    return x;
  }
}

int main() {
  srand(6893274);
  printf("%d\n", p24(0));
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p24(1 << i));
    printf("%d\n", p24((1 << i)-1));
  }
  printf("%d\n", p24(0x800030));
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p24(rand()));
  }

  return 0;
}
