
#include <xmmintrin.h>
#include <cstdlib>
#include <iostream>
#include <cstring>

struct mat44 {
  __m128 r0, r1, r2, r3;
};

template <size_t i>
float E(__m128 data) {
  static_assert(0 <= i && i < 4, "Must extract from lanes 0-3");
  return _mm_cvtss_f32(_mm_shuffle_ps(data, data, _MM_SHUFFLE(i, i, i, i)));
}

__asm__ (
  ".globl transpose44\n\
	.type	transpose44, @function\n\
  transpose44: \n"
  
	"movaps	%xmm0, %xmm5\n\
	unpcklps	%xmm1, %xmm5\n\
	movaps	%xmm2, %xmm4\n\
	unpcklps	%xmm3, %xmm4\n\
	unpckhps	%xmm1, %xmm0\n\
	unpckhps	%xmm3, %xmm2\n\
	movaps	%xmm5, %xmm3\n\
	movlhps	%xmm4, %xmm3\n\
	movhlps	%xmm5, %xmm4\n\
	movaps	%xmm0, %xmm1\n\
	movlhps	%xmm2, %xmm1\n\
	movhlps	%xmm0, %xmm2\n\
	movaps	%xmm4, %xmm0\n\
  retq\n");
  
extern "C" {

 mat44 t(__m128 r0, __m128 r1, __m128 r2, __m128 r3) {
    __asm__ ("call transpose44\n"
             : "=x"(r0), "=x"(r1), "=x"(r2), "=x"(r3)
             : "0"(r0), "1"(r1), "2"(r2), "3"(r3));
    return {r0,r1,r2,r3};
}

}

float rfloat() {
  uint32_t i = rand();
  float f;
  memcpy(&f, &i, sizeof(float));
  return f;
}
__m128 rvect() {
  return _mm_setr_ps(rfloat(), rfloat(), rfloat(), rfloat());
}

int main() {
  for(int i = 0; i < 50; i++) {
    mat44 m = t(rvect(), rvect(), rvect(), rvect());
    //prevent optimization
    std::cout << E<0>(m.r0) << E<1>(m.r1) << E<2>(m.r2) << E<0>(m.r3) << std::endl;
  }
  return 0;
}
