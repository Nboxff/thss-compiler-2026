const int N = 3;

int add(int x, int y) {
  return x + y;
}

int sum(int a[], int n) {
  int i = 0, result = 0;
  while (i < n) {
    result = add(result, a[i]);
    i = i + 1;
  }
  return result;
}

int main() {
  int a[N] = {1, 2, 3};
  int result = sum(a, N);
  {
    int N = 2;
    int a[2] = {4, 5};
    result = add(result, sum(a, N));
    {
      int sum = a[0];
      result = add(result, sum);
    }
    result = add(result, sum(a, N));
  }
  return add(result, sum(a, N));
}
