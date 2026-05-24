.intel_syntax noprefix
.section .data
str0: .asciz "big\n"
str1: .asciz "small\n"

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov rax, 5
    mov [rbp - 16], rax
    mov rax, 0
    mov [rbp - 8], rax
L0:
    mov rax, [rbp - 8]
    cmp rax, [rbp - 16]
    setl al
    movzx rax, al
    mov [rbp - 24], rax
    mov rax, [rbp - 24]
    cmp rax, 0
    je L1
    mov rax, [rbp - 8]
    cmp rax, 2
    setg al
    movzx rax, al
    mov [rbp - 32], rax
    mov rax, [rbp - 32]
    cmp rax, 0
    je L2
    lea rdi, [rip + str0]
    xor eax, eax
    call printf
    jmp L3
L2:
    lea rdi, [rip + str1]
    xor eax, eax
    call printf
L3:
    mov rax, [rbp - 8]
    add rax, 1
    mov [rbp - 40], rax
    mov rax, [rbp - 40]
    mov [rbp - 8], rax
    jmp L0
L1:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
