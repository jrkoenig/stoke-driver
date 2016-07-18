#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p04(int32_t x) {
    int32_t o1 = x - 1;
    return x ^ o1;
  }
}

int main() {
  srand(92837);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p04(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p04(rand()));
  }

  return 0;
}