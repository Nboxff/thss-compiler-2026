int sum(int x, int y, int x, int y) {
  int result = x + y;
  int x;
  {
    int x = 1;
    int y = x + 2;
    result = result + x + y;
  }
  return result + x + y;
}

int first(int a[], int n) {
  int n;
  {
    int n = 0;
    int a = 1;
    n = n + a;
  }
  return a[0] + n;
}

int main() {
  int a[2] = {1, 2};
  int result = sum(1, 2, 3, 4);
  result = result + first(a, 2);
  return result + sum(first(a, 2), 3);
}
