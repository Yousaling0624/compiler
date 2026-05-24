section .data
    str0 db "Enter a number: ", 0
    str1 db "%d", 0
    str2 db "Factorial: %d\n", 0

section .text
    extern printf, scanf

global main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 72
    lea rdi, [str0]
    xor eax, eax
    call printf
    lea rax, [rbp - 24]
    mov [rbp - 32], rax
    lea rdi, [str1]
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
    lea rdi, [str2]
    mov rsi, [rbp - 8]
    xor eax, eax
    call printf
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
