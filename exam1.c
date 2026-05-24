/* 课程设计检查题目 1
 * 将含 struct 的 C 程序翻译为汇编语言
 */
struct student {
    char *name;   // 姓名
    int num;      // 学号
    int age;      // 年龄
    float score;  // 成绩
};

int main() {
    int i;
    int flag;
    int num_140;
    float sum;
    struct student sts[2];

    num_140 = 0;
    sum = 0.0;

    /* 初始化学生数组 */
    sts[0].name = "Li ping";
    sts[0].num = 5;
    sts[0].age = 18;
    sts[0].score = 145.0;

    sts[1].name = "Wang ming";
    sts[1].num = 6;
    sts[1].age = 18;
    sts[1].score = 150.0;

    if (sts[1].score < 140)
        flag = -1;
    else
        flag = 1;

    printf("%d ", flag);
    return 0;
}
