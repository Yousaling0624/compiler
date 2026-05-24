int main() {
    int n;
    int factorial;
    int i;

    printf("Enter a number: ");
    scanf("%d", &n);

    factorial = 1;
    i = 1;
    while (i <= n) {
        factorial = factorial * i;
        i = i + 1;
    }
    printf("Factorial: %d\n", factorial);

    return 0;
}
