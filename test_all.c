int main() {
    int a;
    int b;
    int s;
    int p;
    int d;
    int m;
    int i;
    float f1;
    float f2;
    float f3;

    printf("Enter a: ");
    scanf("%d", &a);
    printf("Enter b: ");
    scanf("%d", &b);

    s = a + b;
    p = a * b;
    d = a / b;
    m = a % b;
    printf("Sum: %d\n", s);
    printf("Product: %d\n", p);
    printf("Division: %d\n", d);
    printf("Modulo: %d\n", m);

    if (a > b)
        printf("a > b\n");
    else
        if (a < b)
            printf("a < b\n");
        else
            printf("a == b\n");

    if (a > 0 && b > 0)
        printf("Both positive\n");

    if (a < 0 || b < 0)
        printf("At least one negative\n");

    printf("While loop: ");
    i = 0;
    while (i < 5) {
        printf("%d ", i);
        i = i + 1;
    }
    printf("\n");

    printf("For loop: ");
    for (i = 10; i >= 1; i = i - 1)
        printf("%d ", i);
    printf("\n");

    f1 = 1.5;
    f2 = 2.5;
    f3 = f1 * f2;
    printf("Float computation done.\n");

    return 0;
}
