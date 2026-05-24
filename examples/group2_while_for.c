int main() {
    int i;
    int j;
    i = 0;
    while (i < 3) {
        for (j = 0; j < 2; j = j + 1)
            printf("%d %d\n", i, j);
        i = i + 1;
    }
    return 0;
}
