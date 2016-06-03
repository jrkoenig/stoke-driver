
#include <cstdlib>
#include <cstdio>


void print_array(int* a, int n) {
    for(int i = 0; i < n; i++) {
        printf("%d ", a[i]);
    }
    printf("\n");
}

extern "C" {
  void reverse(int* a, int n) {
    if (n == 0) return;
    for(int i = 0; i <= (n-1)/2; i++) {
        int *x = a+i;
        int *y = a+n-1-i;
        int t = *x;
        *x = *y;
        *y = t;
    }
  }
}

int main() {
  srand(34232);
  int* arr = new int[10];
  for(int j = 0; j < 10; j++)
    arr[j] = rand();
  reverse(arr, 1);
  print_array(arr,10);
  reverse(arr, 2);
  print_array(arr,10);
  reverse(arr, 2);
  print_array(arr,10);
  
  for(int i = 0; i < 5; i++) {
    for(int j = 0; j < 10; j++)
      arr[j] = rand();
    reverse(arr, 2);
    print_array(arr, 10);
  }
  
  
  for(int i = 0; i < 5; i++) {
    for(int j = 0; j < 10; j++)
      arr[j] = rand();
    reverse(arr, 3);
    print_array(arr, 10);
  }
  
  
  for(int i = 0; i < 20; i++) {
    for(int j = 0; j < 10; j++)
      arr[j] = rand();
    reverse(arr, 3 + rand() % 7);
    print_array(arr, 10);
  }
  return 0;
}
