#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
  int32_t p25(int32_t x, int32_t y) {
    int64_t temp = (int64_t)x * (int64_t)y;
    temp >>= 32;
    return (int32_t) temp;
  }
}

int main() {
  srand(3424637);
  for (int i = 0; i < 50; ++i) {
    printf("%d\n", p25(rand(), rand()));
  }

  return 0;
}
