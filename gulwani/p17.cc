#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p17(int32_t x) {
    int32_t o1 = x - 1;
    int32_t o2 = x | o1;
    int32_t o3 = o2 + 1;
    return o3 & x;
  }
}

int main() {
  srand(782928);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p17(i));
  }
  for (int i = 0; i < 40; ++i) {
    printf("%d\n", p17(rand()));
  }

  return 0;
}
