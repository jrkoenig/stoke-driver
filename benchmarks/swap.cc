
#include <cstdlib>

extern "C" {
  void swap(int* x, int* y) {
	  int t = *x;
	  *x = *y;
	  *y = t;
  }
}
int main() {
  srand(304203);
  int* arr = new int[100];
  for(int i = 0; i < 20; i++) {
    int *x, *y;
    x = arr + rand() % 100;
    y = arr + rand() % 100;
    if (x == y) continue;
    *x = rand();
    *y = rand();
    swap(x,y);
  }
	return 0;
}
