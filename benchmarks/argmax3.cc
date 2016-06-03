
#include <cstdlib>
#include <cstdio>

extern "C" {
  int argmax3(int x, int y, int z) {
	  int m = x < y ? x : y;
    m = m < z ? m : z;
    if (x == m) return 0;
    if (y == m) return 1;
    return 2;
  }
}

int main() {
	printf("%d", argmax3(1,2,3));
	printf("%d", argmax3(2,1,3));
	printf("%d", argmax3(3,2,1));
	printf("%d", argmax3(3,1,2));
	printf("%d", argmax3(2,3,1));
	printf("%d", argmax3(1,3,2));
	
	printf("%d", argmax3(-1,-2,-3));
	printf("%d", argmax3(-2,-1,-3));
	printf("%d", argmax3(-3,-2,-1));
	printf("%d", argmax3(-3,-1,-2));
	printf("%d", argmax3(-2,-3,-1));
	printf("%d", argmax3(-1,-3,-2));
	
	printf("%d", argmax3(-32314345, -342554343, -12133132));
	printf("%d", argmax3(32314345, 342554343, 12133132));
	srand(3426);
	for (int i = 0; i < 50; i++)
	   printf("%d", argmax3(rand(),rand(),rand()));
	return 0;
}
