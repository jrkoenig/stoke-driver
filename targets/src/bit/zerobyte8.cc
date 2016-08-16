['init']
#include "common.h"
extern "C" {
uint32_t zerobyte(uint64_t v)
{
  return (v & 0xFF) == 0;
}
}

void testandprint(uint64_t i) {
  std::cout << "i = " << hexstr(i) << " has zero = " << (zerobyte(i) ? "y": "n") << std::endl;
}

int main() {
  srand32(145874536);
  testandprint(0);
  for(int i = 0; i < 30; i++) {
    auto v = rand64() & 0xFF;
    testandprint(v);
  }
}
