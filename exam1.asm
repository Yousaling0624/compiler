.intel_syntax noprefix
# 课程设计检查题目 1
# 将含 struct 的 C 源程序翻译为汇编语言程序
#
# struct student {
#     char *name;   # 姓名,  offset 0
#     int num;      # 学号,  offset 8
#     int age;      # 年龄,  offset 12
#     float score;  # 成绩,  offset 16
# };
# sizeof(struct student) = 24
#
# int main() {
#     struct student sts[2];
#     int flag;
#     sts[0].name = "Li ping";
#     sts[0].num = 5;
#     sts[0].age = 18;
#     sts[0].score = 145.0;
#     sts[1].name = "Wang ming";
#     sts[1].num = 6;
#     sts[1].age = 18;
#     sts[1].score = 150.0;
#     if (sts[1].score < 140)
#         flag = -1;
#     else
#         flag = 1;
#     printf("%d ", flag);
#     return 0;
# }

.section .data
name0: .asciz "Li ping"
name1: .asciz "Wang ming"
fmt_str: .asciz "%d "

# 浮点常量 (IEEE 754 single precision)
__float_145: .long 1125187584   # 145.0
__float_150: .long 1125515264   # 150.0
__float_140: .long 1124859904   # 140.0

.section .text
.extern printf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 80

    # sts[0] base: rbp-56
    # sts[1] base: rbp-32  (= rbp-56+24)
    # flag:       rbp-8

    # sts[0].name = "Li ping"
    lea rax, [rip + name0]
    mov [rbp - 56], rax

    # sts[0].num = 5
    mov rax, 5
    mov [rbp - 48], rax

    # sts[0].age = 18
    mov rax, 18
    mov [rbp - 44], rax

    # sts[0].score = 145.0
    movss xmm0, [rip + __float_145]
    movss [rbp - 40], xmm0

    # sts[1].name = "Wang ming"
    lea rax, [rip + name1]
    mov [rbp - 32], rax

    # sts[1].num = 6
    mov rax, 6
    mov [rbp - 24], rax

    # sts[1].age = 18
    mov rax, 18
    mov [rbp - 20], rax

    # sts[1].score = 150.0
    movss xmm0, [rip + __float_150]
    movss [rbp - 16], xmm0

    # if (sts[1].score < 140)
    movss xmm0, [rbp - 16]
    movss xmm1, [rip + __float_140]
    ucomiss xmm0, xmm1
    jae else_branch

    # flag = -1
    mov rax, -1
    mov [rbp - 8], rax
    jmp end_if

else_branch:
    # flag = 1
    mov rax, 1
    mov [rbp - 8], rax

end_if:
    # printf("%d ", flag)
    lea rdi, [rip + fmt_str]
    mov rsi, [rbp - 8]
    xor eax, eax
    call printf

    # return 0
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
