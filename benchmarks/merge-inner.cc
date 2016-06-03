
#include <cstdlib>
#include <random>
#include <cassert>
#include <cstdio>

void print_array(int* a, int n) {
    for(int i = 0; i < n; i++) {
        printf("%d ", a[i]);
    }
    printf("\n");
}
extern "C" {
  int inner(int* a, int* b, int*c) {
      if(*a < *b) {
          *c = *a;
          return 1;
      } else {
          *c = *b;
          return 0;
      }
  }
}
bool sorted(int* a, int i, int j) {
  for(int k = i; k < j-1; k++)
    if (a[k] > a[k+1]) return false;
  return true;
}

void merge(int* a, int a_len, int* b, int b_len, int* c) {
    int i = 0;
    int j = 0;
    
    assert(sorted(a, 0, a_len));
    assert(sorted(b, 0, b_len));
    printf("a: "); print_array(a, a_len);
    printf("b: "); print_array(b, b_len);
    while(i < a_len && j < b_len) {
        if (inner(&a[i], &b[j], &c[i+j]))
            i++;
        else 
            j++;
    }
    assert(sorted(c, 0, i+j));
    assert(i == a_len || i == 0 || (a[i] >= c[i+j-1]));
    assert(j == b_len || j == 0 || (b[j] >= c[i+j-1]));
    assert(i == a_len || j == b_len);
    while(i < a_len) {
        c[i+j] = a[i];
        i++;
        assert(sorted(c, 0, i+j));
    }
    while(j < b_len) {
        c[i+j] = b[j];
        j++;
        assert(sorted(c, 0, i+j));
    }
    assert(sorted(c, 0, a_len+b_len));
}

int main() {
    std::default_random_engine gen{};
    std::uniform_int_distribution<int32_t> nums{0,0xFFFFFF};
    gen.seed(2432);
    int* a = new int[10];
    int* b = new int[10];
    int* c = new int[20];
	  merge(a,0,b,0,c);
    for(int i = 0; i < 20; i++) {
	    int accum = 0;
	    for(int j = 0; j < 10; j++) {
	      accum += nums(gen);
	      a[j] = accum;
	    }
	    assert(sorted(a, 0, 10));
        accum = 0;
	    for(int j = 0; j < 10; j++) {
	      accum += nums(gen);
	      b[j] = accum;
	    }
	    assert(sorted(b, 0, 10));
	    merge(a, i % 10, b, (31* i + 423) % 10, c);
    }
    return 0;
}
