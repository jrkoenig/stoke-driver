#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p10(int32_t x, int32_t y) {
    int32_t o1 = x & y;
    int32_t o2 = x ^ y;
    return (uint32_t) o2 <= (uint32_t) o1;
  }
}

int main() {
  srand(2958386);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p10(i, i));
    printf("%d\n", p10(i, i-1));
    printf("%d\n", p10(i, i+1));
  }
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p10(((uint32_t) rand()) >> (rand() %30),
                       ((uint32_t) rand()) >> (rand() %30)));
  }
  for (int i = 0; i < 30; ++i) {
    printf("%d\n", p10(rand(), rand()));
  }

  return 0;
}
