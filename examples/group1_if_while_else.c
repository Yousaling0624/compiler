int main() {
    int i;
    int n;
    n = 3;

    if (n > 0) {
        i = 0;
        while (i < n) {
            printf("%d\n", i);
            i = i + 1;
        }
    } else {
        printf("none\n");
    }
    return 0;
}
