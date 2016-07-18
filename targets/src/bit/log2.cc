
#include "common.h"

extern "C" {
uint32_t log_2(uint32_t v) {
  v |= (v >> 1);
  v |= (v >> 2);
  v |= (v >> 4);
  v |= (v >> 8);
  v |= (v >> 16);

  int count = 0;
  while (v) {
    count += v & 1;
    v >>= 1;
  }
  return count - 1;
}
}

void testandprint(uint32_t i) {
  std::cout << "i = " << binstr(i) << "; log2(i) = " << log_2(i) << std::endl;
}

int main() {
  srand32(16741023);
  for(int i = 0; i < 10; i++) {
    testandprint(i);
  }
  for(int i = 0; i < 31; i += 3) {
    testandprint(((uint32_t)-1) >> i);
  }
  for(int i = 0; i < 30; i += 3) {
    testandprint(((uint32_t)1) << i);
  }
  for(int i = 0; i < 40; i++) {
    testandprint(rand32() >> (rand32() % 31));
  }
}
