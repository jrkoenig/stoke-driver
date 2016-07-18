
#include "common.h"
extern "C" {
uint64_t revbytes(uint64_t v)
{
  uint64_t r = 0;
  for(int i = 0; i < 8; i++) {
    uint8_t x = (v >> (i*8)) & 0xFF;
    x = (((x & 0xaa) >> 1) | ((x & 0x55) << 1));
  	x = (((x & 0xcc) >> 2) | ((x & 0x33) << 2));
  	x = (((x & 0xf0) >> 4) | ((x & 0x0f) << 4));
    r |= ((uint64_t)x) << (i*8);
  }
  return r;
}
}

void testandprint(uint64_t i) {
  std::cout << "                 --------========--------========--------========--------========"<< "\n";
  std::cout << "           i = " << binstr(i) << "\n revbytes(i) = " << binstr(revbytes(i)) << "\n" << std::endl;
  assert(revbytes(revbytes(i)) == i);
}

int main() {
  srand32(145874536);
  testandprint(0);
  testandprint(-1);
  for(int i = 0; i < 10; i++) {
    testandprint(rand32() & 0xFF);
  }
  for(int i = 0; i < 10; i++) {
    testandprint(rand32() & 0xFF00);
  }
  for(int i = 0; i < 40; i++) {
    testandprint(rand64());
  }
}
