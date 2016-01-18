#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p03(int32_t x) {
    int32_t o1 = -x;
    return x & o1;
  }
}

int main() {
  srand(1420);
  for (int i = -10; i < 10; ++i) {
    printf("%d\n", p03(i));
  }
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p03(rand()));
  }

  return 0;
}
