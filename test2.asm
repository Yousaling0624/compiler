.intel_syntax noprefix
.section .data
str0: .asciz "Division: %d\n"
str1: .asciz "Modulo: %d\n"
str2: .asciz "Flag is true\n"
str3: .asciz "Wont print\n"
str4: .asciz "Not flag\n"
str5: .asciz "Both positive\n"
str6: .asciz "At least one condition\n"
str7: .asciz "Negation: %d\n"
str8: .asciz "Nested if: a negative, b positive\n"

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 128
    mov rax, 10
    mov [rbp - 8], rax
    mov rax, 3
    mov [rbp - 16], rax
    xor edx, edx
    mov rax, [rbp - 8]
    cqo
    mov rcx, [rbp - 16]
    idiv rcx
    mov [rbp - 40], rax
    mov rax, [rbp - 40]
    mov [rbp - 32], rax
    lea rdi, [rip + str0]
    mov rsi, [rbp - 32]
    xor eax, eax
    call printf
    xor edx, edx
    mov rax, [rbp - 8]
    cqo
    mov rcx, [rbp - 16]
    idiv rcx
    mov [rbp - 48], rdx
    mov rax, [rbp - 48]
    mov [rbp - 32], rax
    lea rdi, [rip + str1]
    mov rsi, [rbp - 32]
    xor eax, eax
    call printf
    mov rax, 1
    mov [rbp - 24], rax
    mov rax, [rbp - 24]
    cmp rax, 0
    je L0
    lea rdi, [rip + str2]
    xor eax, eax
    call printf
L0:
    mov rax, [rbp - 24]
    cmp rax, 0
    sete al
    movzx rax, al
    mov [rbp - 64], rax
    mov rax, [rbp - 64]
    cmp rax, 0
    je L1
    lea rdi, [rip + str3]
    xor eax, eax
    call printf
    jmp L2
L1:
    lea rdi, [rip + str4]
    xor eax, eax
    call printf
L2:
    mov rax, [rbp - 8]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 72], rax
    mov rax, [rbp - 72]
    cmp rax, 0
    je L3
    mov rax, [rbp - 16]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 80], rax
    mov rax, [rbp - 80]
    cmp rax, 0
    je L3
    lea rdi, [rip + str5]
    xor eax, eax
    call printf
L3:
    mov rax, [rbp - 8]
    cmp rax, 0
    setl al
    movzx rax, al
    mov [rbp - 88], rax
    mov rax, [rbp - 88]
    cmp rax, 0
    jne L5
    mov rax, [rbp - 16]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 96], rax
    mov rax, [rbp - 96]
    cmp rax, 0
    je L4
L5:
    lea rdi, [rip + str6]
    xor eax, eax
    call printf
L4:
    mov rax, 5
    neg rax
    mov [rbp - 104], rax
    mov rax, [rbp - 104]
    mov [rbp - 8], rax
    mov rax, [rbp - 8]
    neg rax
    mov [rbp - 112], rax
    mov rax, [rbp - 112]
    mov [rbp - 16], rax
    lea rdi, [rip + str7]
    mov rsi, [rbp - 16]
    xor eax, eax
    call printf
    mov rax, [rbp - 8]
    cmp rax, 0
    setl al
    movzx rax, al
    mov [rbp - 120], rax
    mov rax, [rbp - 120]
    cmp rax, 0
    je L6
    mov rax, [rbp - 16]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 56], rax
    mov rax, [rbp - 56]
    cmp rax, 0
    je L7
    lea rdi, [rip + str8]
    xor eax, eax
    call printf
L7:
L6:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
