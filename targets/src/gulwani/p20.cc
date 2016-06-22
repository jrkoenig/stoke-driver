#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p20(int32_t x) {
    int32_t o1 = -x;
    int32_t o2 = x & o1;
    int32_t o3 = x + o2;
    int32_t o4 = x ^ o2;
    int32_t o5 = o4 >> 2;
    int32_t o6 = o5 / o2;
    return o3 | o6;
  }
}

int main() {
  srand(927463);
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p20(i+1));
  }
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p20(rand()+1));
  }

  return 0;
}
