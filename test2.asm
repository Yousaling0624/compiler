section .data
    str0 db "Division: %d\n", 0
    str1 db "Modulo: %d\n", 0
    str2 db "Flag is true\n", 0
    str3 db "Wont print\n", 0
    str4 db "Not flag\n", 0
    str5 db "Both positive\n", 0
    str6 db "At least one condition\n", 0
    str7 db "Negation: %d\n", 0
    str8 db "Nested if: a negative, b positive\n", 0

section .text
    extern printf, scanf

global main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 136
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
    lea rdi, [str0]
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
    lea rdi, [str1]
    mov rsi, [rbp - 32]
    xor eax, eax
    call printf
    mov rax, 1
    mov [rbp - 24], rax
    mov rax, [rbp - 24]
    cmp rax, 0
    je L0
    lea rdi, [str2]
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
    lea rdi, [str3]
    xor eax, eax
    call printf
    jmp L2
L1:
    lea rdi, [str4]
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
    lea rdi, [str5]
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
    lea rdi, [str6]
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
    lea rdi, [str7]
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
    lea rdi, [str8]
    xor eax, eax
    call printf
L7:
L6:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
