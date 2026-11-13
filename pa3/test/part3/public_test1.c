const int N = 3;

int add(int a, int b) {
  return a + b;
}

int fib(int n) {
  if (n <= 1) {
    return n;
  }
  return fib(n - 1) + fib(n - 2);
}

void printSum(int a, int b) {
  int s = add(a, b);
}

int main() {
  int x = add(1, 2);
  int y = add(x, 3);
  printSum(x, fib(N));
  return 0;
}

int twice(int x) {
  return add(x, x);
}

void unused() {
  return;
}
