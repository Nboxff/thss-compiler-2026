int cond(int x) {
  return x;
}

void body() {
}

void step() {
}

int main() {
  int i = 0;
  while (cond(i)) {
    body();
    i = i + 1;
  }
  if (cond(i)) {
    step();
  } else {
    body();
  }
  return 0;
}
