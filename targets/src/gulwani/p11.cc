#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p11(int32_t x, int32_t y) {
    int32_t o1 = ~y;
    int32_t o2 = x & o1;
    return (uint32_t) o2 > (uint32_t) y;
  }
}

int main() {
  srand(8064930);
  for (int i = 0; i < 50; ++i) {
    printf("%d\n", p11(rand(), rand()));
  }
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p11(i, i));
    printf("%d\n", p11(i, i-1));
    printf("%d\n", p11(i, i+1));
  }

  return 0;
}
