int idx() { return 0; }
int val() { return 1; }

int main() {
  int a[2];
  a[idx()] = val();
  return a[idx()];
}
