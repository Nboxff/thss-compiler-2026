int fact(int n) {
  if (n <= 1) {
    return 1;
  }
  return n * fact(n - 1);
}

int ping(int n) {
  if (n <= 0) {
    return 0;
  }
  return fact(n - 1) + ping(n - 1);
}

int pong(int n) {
  if (n <= 0) {
    return 0;
  }
  return ping(n - 1);
}

int main() {
  return fact(3) + pong(2);
}
