
#include "common.h"

extern "C" {
uint32_t rev32(uint32_t v)
{
  uint32_t r = v & 1;
  for(int i = 0; i < 31; i++) {
    v >>= 1;
    r <<= 1;
    r |= v & 1;
  }
  return r;
}
}

void testandprint(uint32_t i) {
  std::cout << "        i = " << binstr(i) << "\n rev32(i) = " << binstr(rev32(i)) << "\n" << std::endl;
  assert(rev32(rev32(i)) == i);
}

int main() {
  srand32(845973645);
  for(int i = 0; i < 10; i++) {
    testandprint(i);
  }
  for(int i = 0; i < 31; i += 3) {
    testandprint(((uint32_t)-1) >> i);
  }
  for(int i = 0; i < 40; i++) {
    testandprint(rand32());
  }
}
