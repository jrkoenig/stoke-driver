
#include <cstdlib>
#include <random>
#include <cassert>
#include <cstdio>
extern "C" {
    void inc(int* a, int n) {
        for(int i = 0; i < n; i++)
            a[i] ++;
    }
}

void print_array(int* a, int n) {
    for(int i = 0; i < n; i++) {
        printf("%d ", a[i]);
    }
    printf("\n");
}

int main() {
    std::default_random_engine gen{};
    std::uniform_int_distribution<int32_t> nums{0,0xFFFFFF};
    gen.seed(2432);
    int* a = new int[10];
    int* b = new int[10];
    int* c = new int[10];
    for(int i = 1; i < 10; i++) {
	    for(int j = 0; j < 10; j++) {
	      a[j] = nums(gen);
	      b[j] = nums(gen);
	      c[j] = nums(gen);
	    }
	    inc(a, i);
	    print_array(a, 10);
	    inc(b, i);
	    print_array(b, 10);
	    inc(c, i);
	    print_array(c, 10);
    }
    return 0;
}
