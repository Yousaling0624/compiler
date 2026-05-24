int main() {
    int i;
    int n;
    n = 5;

    if (n <= 0) {
        printf("none\n");
    } else {
        for (i = 0; i < n; i = i + 1)
            printf("%d\n", i);
    }
    return 0;
}
