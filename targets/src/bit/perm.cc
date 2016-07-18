
#include "common.h"

extern "C" {
uint32_t perm(uint32_t v)
{
  uint32_t t = v | (v - 1);
  return (t + 1) | (((~t & -~t) - 1) >> (__builtin_ctz(v) + 1));
}
}

uint32_t testandprint(uint32_t i) {
  auto p = perm(i);
  std::cout << "i = " << binstr(i) << "; perm = " << binstr(p) << std::endl;
  return p;
}

int main() {
  srand32(95362418);
  for(int i = 0; i < 5; i++) {
    testandprint(i);
    testandprint(i << 20);
  }
  uint32_t v = 1;
  for(int i = 0; i < 20; i++) {
    v = testandprint(v);
  }
  v = 13;
  for(int i = 0; i < 20; i++) {
    v = testandprint(v);
  }
  for(int i = 0; i < 10; i++) {
    testandprint(rand32());
    testandprint(rand32() & rand32());
    testandprint(rand32() & rand32() & rand32());
  }
}
