.intel_syntax noprefix
.section .data
str0: .asciz "Enter two integers: "
str1: .asciz "%d %d"
str10: .asciz "Float addition done.\n"
str2: .asciz "Sum: %d\n"
str3: .asciz "Product: %d\n"
str4: .asciz "a is greater than b\n"
str5: .asciz "a is not greater than b\n"
str6: .asciz "Counting up:\n"
str7: .asciz "%d\n"
str8: .asciz "Counting down with for:\n"
str9: .asciz "%d\n"
__float0: .long 1078523331
__float1: .long 1075838976

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 160
    lea rdi, [rip + str0]
    xor eax, eax
    call printf
    lea rax, [rbp - 8]
    mov [rbp - 56], rax
    lea rax, [rbp - 16]
    mov [rbp - 64], rax
    lea rdi, [rip + str1]
    mov rsi, [rbp - 56]
    mov rdx, [rbp - 64]
    xor eax, eax
    call scanf
    mov rax, [rbp - 8]
    add rax, [rbp - 16]
    mov [rbp - 80], rax
    mov rax, [rbp - 80]
    mov [rbp - 48], rax
    mov rax, [rbp - 8]
    imul rax, [rbp - 16]
    mov [rbp - 88], rax
    mov rax, [rbp - 88]
    mov [rbp - 40], rax
    lea rdi, [rip + str2]
    mov rsi, [rbp - 48]
    xor eax, eax
    call printf
    lea rdi, [rip + str3]
    mov rsi, [rbp - 40]
    xor eax, eax
    call printf
    mov rax, [rbp - 8]
    sub rax, [rbp - 16]
    mov [rbp - 96], rax
    mov rax, [rbp - 96]
    mov [rbp - 24], rax
    mov rax, [rbp - 24]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 104], rax
    mov rax, [rbp - 104]
    cmp rax, 0
    je L0
    lea rdi, [rip + str4]
    xor eax, eax
    call printf
    jmp L1
L0:
    lea rdi, [rip + str5]
    xor eax, eax
    call printf
L1:
    lea rdi, [rip + str6]
    xor eax, eax
    call printf
    mov rax, 1
    mov [rbp - 32], rax
L2:
    mov rax, [rbp - 32]
    cmp rax, 5
    setle al
    movzx rax, al
    mov [rbp - 112], rax
    mov rax, [rbp - 112]
    cmp rax, 0
    je L3
    lea rdi, [rip + str7]
    mov rsi, [rbp - 32]
    xor eax, eax
    call printf
    mov rax, [rbp - 32]
    add rax, 1
    mov [rbp - 120], rax
    mov rax, [rbp - 120]
    mov [rbp - 32], rax
    jmp L2
L3:
    lea rdi, [rip + str8]
    xor eax, eax
    call printf
    mov rax, 5
    mov [rbp - 32], rax
L4:
    mov rax, [rbp - 32]
    cmp rax, 1
    setge al
    movzx rax, al
    mov [rbp - 128], rax
    mov rax, [rbp - 128]
    cmp rax, 0
    je L5
    lea rdi, [rip + str9]
    mov rsi, [rbp - 32]
    xor eax, eax
    call printf
    mov rax, [rbp - 32]
    sub rax, 1
    mov [rbp - 136], rax
    mov rax, [rbp - 136]
    mov [rbp - 32], rax
    jmp L4
L5:
    movss xmm0, [rip + __float0]
    movss [rbp - 144], xmm0
    movss xmm0, [rip + __float1]
    movss [rbp - 152], xmm0
    movss xmm0, [rbp - 144]
    addss xmm0, [rbp - 152]
    movss [rbp - 72], xmm0
    movss xmm0, [rbp - 72]
    movss [rbp - 160], xmm0
    lea rdi, [rip + str10]
    xor eax, eax
    call printf
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
