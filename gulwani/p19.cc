#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p19(int32_t x, int32_t m, int32_t k) {
    int32_t o1 = x >> k;
    int32_t o2 = x ^ o1;
    int32_t o3 = o2 & m;
    int32_t o4 = o3 << k;
    int32_t o5 = o4 ^ o3;
    return o5 ^ x;
  }
}

int main() {
  srand(50243);
  for (size_t i = 0; i < 20; ++i) {
    printf("%d\n", p19(rand(), i, rand() % 31));
  }

  return 0;
}
