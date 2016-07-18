
#include "common.h"
extern "C" {
uint32_t morton(uint16_t a, uint16_t b)
{
  uint32_t c = 0;

  for (int i = 0; i < 16; i++) {
    c |= (a & 1U << i) << i | (b & 1U << i) << (i + 1);
  }
  return c;
}
}
void testandprint(uint16_t i, uint16_t j) {
  std::cout << "i = " << binstr(i) << " j = " << binstr(j) << " morton(i,j) = " << binstr(morton(i,j))  << std::endl;
}

int main() {
  srand32(731561861);
  testandprint(0,0);
  testandprint(1,1);
  testandprint(2,2);
  testandprint(-1,-1);
  testandprint(-2,-2);
  for (int i = 0; i < 5; i++) {
    auto a = rand32(), b = rand32();
    testandprint(a, 0);
    testandprint(0, b);
    testandprint(-1, b);
    testandprint(a, -1);
    testandprint(a, b);
  }
  for (int i = 0; i < 20; i++) {
    auto a = rand32(), b = rand32();
    testandprint(a, b);
  }
}
