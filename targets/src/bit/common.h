
#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <iostream>
#include <cassert>
#include <random>
#include <cstring>

#include <sstream>
#include <bitset>
#include <iomanip>

std::mt19937 generator{};

void srand32(uint32_t seed) {
  generator.seed();
}
uint32_t rand32() {
  return generator();
}
uint64_t rand64() {
  return generator() | (((uint64_t)generator()) << 32);
}

std::string hexstr(uint8_t x) {
  std::stringstream s;
  s << "0x" << std::setfill('0') << std::setw(2) << std::hex << x;
  return s.str();
}

std::string binstr(uint8_t x) {
  std::stringstream s;
  s << "0b" << std::bitset<8>(x);
  return s.str();
}


std::string hexstr(uint16_t x) {
  std::stringstream s;
  s << "0x" << std::setfill('0') << std::setw(4) << std::hex << x;
  return s.str();
}

std::string binstr(uint16_t x) {
  std::stringstream s;
  s << "0b" << std::bitset<16>(x);
  return s.str();
}

std::string hexstr(uint32_t x) {
  std::stringstream s;
  s << "0x" << std::setfill('0') << std::setw(8) << std::hex << x;
  return s.str();
}

std::string binstr(uint32_t x) {
  std::stringstream s;
  s << "0b" << std::bitset<32>(x);
  return s.str();
}

std::string hexstr(uint64_t x) {
  std::stringstream s;
  s << "0x" << std::setfill('0') << std::setw(16) << std::hex << x;
  return s.str();
}

std::string binstr(uint64_t x) {
  std::stringstream s;
  s << "0b" << std::bitset<64>(x);
  return s.str();
}
