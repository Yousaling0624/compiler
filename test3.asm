.intel_syntax noprefix
.section .data
str0: .asciz "Enter a number: "
str1: .asciz "%d"
str2: .asciz "Factorial: %d\n"

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    lea rdi, [rip + str0]
    xor eax, eax
    call printf
    lea rax, [rbp - 24]
    mov [rbp - 32], rax
    lea rdi, [rip + str1]
    mov rsi, [rbp - 32]
    xor eax, eax
    call scanf
    mov rax, 1
    mov [rbp - 8], rax
    mov rax, 1
    mov [rbp - 16], rax
L0:
    mov rax, [rbp - 16]
    cmp rax, [rbp - 24]
    setle al
    movzx rax, al
    mov [rbp - 40], rax
    mov rax, [rbp - 40]
    cmp rax, 0
    je L1
    mov rax, [rbp - 8]
    imul rax, [rbp - 16]
    mov [rbp - 48], rax
    mov rax, [rbp - 48]
    mov [rbp - 8], rax
    mov rax, [rbp - 16]
    add rax, 1
    mov [rbp - 56], rax
    mov rax, [rbp - 56]
    mov [rbp - 16], rax
    jmp L0
L1:
    lea rdi, [rip + str2]
    mov rsi, [rbp - 8]
    xor eax, eax
    call printf
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
