#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p06(int32_t x) {
    int32_t o1 = x + 1;
    return x | o1;
  }
}

int main() {
  srand(766052);
  p06(0xFFFF);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p06(rand()));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p06(rand()));
  }

  return 0;
}
