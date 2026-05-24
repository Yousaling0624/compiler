int main() {
    int a;
    int b;
    int c;
    int sum;
    int product;
    int i;
    float x;
    float y;
    float z;

    printf("Enter two integers: ");
    scanf("%d %d", &a, &b);

    sum = a + b;
    product = a * b;
    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);

    c = a - b;
    if (c > 0)
        printf("a is greater than b\n");
    else
        printf("a is not greater than b\n");

    printf("Counting up:\n");
    i = 1;
    while (i <= 5) {
        printf("%d\n", i);
        i = i + 1;
    }

    printf("Counting down with for:\n");
    for (i = 5; i >= 1; i = i - 1)
        printf("%d\n", i);

    x = 3.14;
    y = 2.5;
    z = x + y;
    printf("Float addition done.\n");

    return 0;
}
