
#include "common.h"

extern "C" {
  uint32_t gray(uint32_t g)
  {
    g ^= (g >> 16);
    g ^= (g >> 8);
    g ^= (g >> 4);
    g ^= (g >> 2);
    g ^= (g >> 1);
    return g;
  }
}

void testandprint(uint32_t i) {
  i = i & 0xFF;
  auto g = gray(i ^ (i >> 1));
  std::cout << "i="<< i << "; code=" << hexstr(i ^ (i>>1)) << "; ungray = " << g << std::endl;
  assert(g == i);
}

int main() {
  srand32(95362418);
  for(int i = -5; i < 5; i++) {
    testandprint(i);
    testandprint(i*2);
    testandprint(i*5);
  }
  for(int i = 0; i < 30; i++) {
    testandprint(rand32());
    testandprint(rand32() & rand32());
    testandprint(rand32() | rand32());
  }
}
