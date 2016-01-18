#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p21(int32_t x, int32_t a, int32_t b, int32_t c) {
    int32_t o1 = -(x == c);
    int32_t o2 = a ^ c;
    int32_t o3 = -(x == a);
    int32_t o4 = b ^ c;
    int32_t o5 = o1 & o2;
    int32_t o6 = o3 & o4;
    int32_t o7 = o5 ^ o6;
    return o7 ^ c;
  }
}

int main() {
  srand(3860342);
  for (int i = 0; i < 50; ++i) {
    int32_t a = rand();
    int32_t b = rand();
    int32_t c = rand();
    int32_t x = 0;
    switch (rand() % 3) {
      case 0: x = a; break;
      case 1: x = b; break;
      case 2: x = c; break;
    }
    printf("%d\n", p21(x, a, b, c));
  }

  return 0;
}
