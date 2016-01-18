#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p02(int32_t x) {
    int32_t o1 = x + 1;
    return x & o1;
  }
}

int main() {
  srand(75624);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p02(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p02(rand()));
  }

  return 0;
}
