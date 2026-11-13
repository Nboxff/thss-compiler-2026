int a() { return 1; }
int b() { return a(); }
int c() { return b(); }

int main() {
  return c();
}
