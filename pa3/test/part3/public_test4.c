int f(int x) {
  return x;
}

int g(int x) {
  return x;
}

int h(int x) {
  return x;
}

int main() {
  return f(g(1)) + h(2);
}
