#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

extern "C" {
  int32_t p01(int32_t x) {
    int32_t o1 = x - 1;
    return x & o1;
  }
}

int main() {
  srand(244245);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p01(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p01(rand()));
  }
  return 0;
}
