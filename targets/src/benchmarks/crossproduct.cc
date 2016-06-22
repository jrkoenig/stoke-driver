
#include <iostream>
#include <cstdlib>
#include <xmmintrin.h>

__m128 vec3(float x, float y, float z) {
  return _mm_set_ps(z, z, y, x);
}

float first(__m128 v) {
  return _mm_cvtss_f32(v);
}

extern "C" {


__m128 cross(__m128 a, __m128 b) {
  float ax = _mm_cvtss_f32(_mm_shuffle_ps(a, a, _MM_SHUFFLE(0, 0, 0, 0)));
  float ay = _mm_cvtss_f32(_mm_shuffle_ps(a, a, _MM_SHUFFLE(1, 1, 1, 1)));
  float az = _mm_cvtss_f32(_mm_shuffle_ps(a, a, _MM_SHUFFLE(2, 2, 2, 2)));
  float bx = _mm_cvtss_f32(_mm_shuffle_ps(b, b, _MM_SHUFFLE(0, 0, 0, 0)));
  float by = _mm_cvtss_f32(_mm_shuffle_ps(b, b, _MM_SHUFFLE(1, 1, 1, 1)));
  float bz = _mm_cvtss_f32(_mm_shuffle_ps(b, b, _MM_SHUFFLE(2, 2, 2, 2)));
  
  return _mm_setr_ps(ay*bz-az*by,
                     az*bx-ax*bz,
                     ax*by-az*bx,0);
 }
};

float rfloat() {
  return -100.0f + (200.0f *rand())/RAND_MAX;
}
__m128 rvect() {
  return _mm_set_ps(rfloat(), rfloat(), rfloat(), rfloat());
}

int main() {
  
    auto v = cross(vec3(1,-8,0), vec3(12,20,0));
    //prevent optimization
    std::cout << first(v) << std::endl;
    v = (cross(vec3(0,-6,0), vec3(4,3,0)));
    std::cout << first(v) << std::endl;
    v = (cross(vec3(0,0,0), vec3(0,0,0)));
    std::cout << first(v) << std::endl;
    v = (cross(vec3(-1,0,0), vec3(0,0,1)));
    std::cout << first(v) << std::endl;
    v = (cross(vec3(0,0,1), vec3(0,1,0)));
    std::cout << first(v) << std::endl;
    
    for(int i = 0; i < 50; i++) {
      v = (cross(rvect(), rvect()));
      //prevent optimization
      std::cout << first(v) << std::endl;
    }
    return 0;
  
}
