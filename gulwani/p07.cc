#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p07(int32_t x) {
    int32_t o1 = ~x;
    int32_t o2 = x + 1;
    return o1 & o2;
  }
}

int main() {
  srand(9173527);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p07(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p07(rand()));
  }

  return 0;
}
