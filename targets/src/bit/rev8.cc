
#include "common.h"

extern "C" {
uint8_t rev8(uint8_t v)
{
  uint32_t r = v & 1;
  for(int i = 0; i < 7; i++) {
    v >>= 1;
    r <<= 1;
    r |= v & 1;
  }
  return r;
}
}

void testandprint(uint8_t i) {
  i = i & 0xFF;
  std::cout << "        i = " << binstr(i) << "\n rev32(i) = " << binstr(rev8(i)) << "\n" << std::endl;
  assert(rev8(rev8(i)) == i);
}

int main() {
  for(int i = 0; i < 256; i++) {
    testandprint(i);
  }
}
