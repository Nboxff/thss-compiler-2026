int main() {
  int a[3];
  int i = 0;
  while (i < 3) {
    a[i] = i;
    i = i + 1;
  }
  return a[0];
}
