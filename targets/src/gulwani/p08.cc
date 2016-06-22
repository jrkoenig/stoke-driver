#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p08(int32_t x) {
    int32_t o1 = x - 1;
    int32_t o2 = ~x;
    return o1 & o2;
  }
}

int main() {
  srand(3425243);
  for (int i = -10; i < 10; ++i) {
    printf("%d\n", p08(i));
  }
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p08(rand()));
  }

  return 0;
}
