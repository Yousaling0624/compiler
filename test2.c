int main() {
    int a;
    int b;
    int result;
    int flag;

    a = 10;
    b = 3;

    result = a / b;
    printf("Division: %d\n", result);

    result = a % b;
    printf("Modulo: %d\n", result);

    flag = 1;
    if (flag)
        printf("Flag is true\n");

    if (!flag)
        printf("Wont print\n");
    else
        printf("Not flag\n");

    if (a > 0 && b > 0)
        printf("Both positive\n");

    if (a < 0 || b > 0)
        printf("At least one condition\n");

    a = -5;
    b = -a;
    printf("Negation: %d\n", b);

    if (a < 0)
        if (b > 0)
            printf("Nested if: a negative, b positive\n");

    return 0;
}
