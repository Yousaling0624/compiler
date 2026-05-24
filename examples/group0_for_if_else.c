int main() {
    int i;
    int n;
    n = 5;
    for (i = 0; i < n; i = i + 1) {
        if (i > 2)
            printf("big\n");
        else
            printf("small\n");
    }
    return 0;
}
