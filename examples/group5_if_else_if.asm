.intel_syntax noprefix
.section .data
str0: .asciz "positive\n"
str1: .asciz "negative\n"

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rax, 10
    mov [rbp - 24], rax
    mov rax, [rbp - 24]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 8], rax
    mov rax, [rbp - 8]
    cmp rax, 0
    je L0
    lea rdi, [rip + str0]
    xor eax, eax
    call printf
    jmp L1
L0:
    mov rax, [rbp - 24]
    cmp rax, 0
    setl al
    movzx rax, al
    mov [rbp - 16], rax
    mov rax, [rbp - 16]
    cmp rax, 0
    je L2
    lea rdi, [rip + str1]
    xor eax, eax
    call printf
L2:
L1:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
