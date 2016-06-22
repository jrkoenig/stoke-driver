
#include <cstdlib>
#include <cstdio>

extern "C" {
  int argmax(int x, int y) {
	  if (x < y) return 1;
	  return 0;
  }
}
int main() {
	printf("%d", argmax(3, 6));
	printf("%d", argmax(7,2));
	printf("%d", argmax(4,4));
	printf("%d", argmax(-1,0));
	printf("%d", argmax(-4,-299392));
	printf("%d", argmax(0xF0FF1234, 0xFF0F1234));
	printf("%d", argmax(0xFF0F1234, 0xF0FF1234));
	printf("%d", argmax(-342,-65));
	printf("%d", argmax(2342524,2342523));
	printf("%d", argmax(2342524,2342525));
	for (int i =-4; i< 4; i++)
		for(int j = -4; j < 4; j++) {
			printf("%d", argmax(i*32434,j*124225));
		}
	return 0;
}

