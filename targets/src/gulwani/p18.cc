#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

extern "C" {
  int32_t p18(int32_t x) {
    int32_t o1 = x - 1;
    int32_t o2 = o1 & x;
    int32_t o3 = !!x;
    int32_t o4 = !!o2;
    int32_t o5 = !o4;
    return o5 && o3;
  }
}

int main() {
  srand(79724953);
  for (int i = 0; i < 10; ++i) {
    printf("%d\n", p18(1 << i));
    printf("%d\n", p18((1 << i)+1));
    printf("%d\n", p18((1 << i)-1));
  }
  for (int i = 0; i < 20; ++i) {
    printf("%d\n", p18(rand()));
  }

  return 0;
}
