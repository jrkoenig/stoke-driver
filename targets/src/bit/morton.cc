
#include "common.h"
extern "C" {
  uint32_t morton(uint16_t a, uint16_t b)
  {
    const unsigned int B[] = {0x55555555, 0x33333333, 0x0F0F0F0F, 0x00FF00FF};
    const unsigned int S[] = {1, 2, 4, 8};
    uint32_t x = a, y = b;

    x = (x | (x << S[3])) & B[3];
    x = (x | (x << S[2])) & B[2];
    x = (x | (x << S[1])) & B[1];
    x = (x | (x << S[0])) & B[0];

    y = (y | (y << S[3])) & B[3];
    y = (y | (y << S[2])) & B[2];
    y = (y | (y << S[1])) & B[1];
    y = (y | (y << S[0])) & B[0];

    return x | (y << 1);

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
    auto a = rand16(), b = rand16();
    testandprint(a, 0);
    testandprint(0, b);
    testandprint(-1, b);
    testandprint(a, -1);
    testandprint(a, b);
  }
  for (int i = 0; i < 20; i++) {
    auto a = rand16(), b = rand16();
    testandprint(a, b);
  }
}
