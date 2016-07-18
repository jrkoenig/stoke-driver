
#include "common.h"
extern "C" {
uint32_t zerobyte(uint64_t v)
{
  for(int i = 0; i < 8; i++)
    if (((v >> (i * 8)) & 0xFF) == 0)
      return 1;
  return 0;
}
}

void testandprint(uint64_t i) {
  std::cout << "i = " << hexstr(i) << " has zero = " << (zerobyte(i) ? "y": "n") << std::endl;
}

int main() {
  srand32(145874536);
  testandprint(0);
  testandprint(-1);
  for(int i = 0; i < 100; i++) {
    auto v = rand64();
    auto which = rand32() % 8;
    testandprint(v);
    testandprint(v & ~ (((uint64_t)0xFF) << (which*8)));
  }
}
