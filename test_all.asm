.intel_syntax noprefix
.section .data
str0: .asciz "Enter a: "
str1: .asciz "%d"
str10: .asciz "a == b\n"
str11: .asciz "Both positive\n"
str12: .asciz "At least one negative\n"
str13: .asciz "While loop: "
str14: .asciz "%d "
str15: .asciz "\n"
str16: .asciz "For loop: "
str17: .asciz "%d "
str18: .asciz "\n"
str19: .asciz "Float computation done.\n"
str2: .asciz "Enter b: "
str3: .asciz "%d"
str4: .asciz "Sum: %d\n"
str5: .asciz "Product: %d\n"
str6: .asciz "Division: %d\n"
str7: .asciz "Modulo: %d\n"
str8: .asciz "a > b\n"
str9: .asciz "a < b\n"
__float0: .long 1069547520
__float1: .long 1075838976

.section .text
.extern printf
.extern scanf

.globl main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 224
    lea rdi, [rip + str0]
    xor eax, eax
    call printf
    lea rax, [rbp - 8]
    mov [rbp - 88], rax
    lea rdi, [rip + str1]
    mov rsi, [rbp - 88]
    xor eax, eax
    call scanf
    lea rdi, [rip + str2]
    xor eax, eax
    call printf
    lea rax, [rbp - 16]
    mov [rbp - 96], rax
    lea rdi, [rip + str3]
    mov rsi, [rbp - 96]
    xor eax, eax
    call scanf
    mov rax, [rbp - 8]
    add rax, [rbp - 16]
    mov [rbp - 160], rax
    mov rax, [rbp - 160]
    mov [rbp - 80], rax
    mov rax, [rbp - 8]
    imul rax, [rbp - 16]
    mov [rbp - 168], rax
    mov rax, [rbp - 168]
    mov [rbp - 72], rax
    xor edx, edx
    mov rax, [rbp - 8]
    cqo
    mov rcx, [rbp - 16]
    idiv rcx
    mov [rbp - 176], rax
    mov rax, [rbp - 176]
    mov [rbp - 24], rax
    xor edx, edx
    mov rax, [rbp - 8]
    cqo
    mov rcx, [rbp - 16]
    idiv rcx
    mov [rbp - 184], rdx
    mov rax, [rbp - 184]
    mov [rbp - 64], rax
    lea rdi, [rip + str4]
    mov rsi, [rbp - 80]
    xor eax, eax
    call printf
    lea rdi, [rip + str5]
    mov rsi, [rbp - 72]
    xor eax, eax
    call printf
    lea rdi, [rip + str6]
    mov rsi, [rbp - 24]
    xor eax, eax
    call printf
    lea rdi, [rip + str7]
    mov rsi, [rbp - 64]
    xor eax, eax
    call printf
    mov rax, [rbp - 8]
    cmp rax, [rbp - 16]
    setg al
    movzx rax, al
    mov [rbp - 192], rax
    mov rax, [rbp - 192]
    cmp rax, 0
    je L0
    lea rdi, [rip + str8]
    xor eax, eax
    call printf
    jmp L1
L0:
    mov rax, [rbp - 8]
    cmp rax, [rbp - 16]
    setl al
    movzx rax, al
    mov [rbp - 200], rax
    mov rax, [rbp - 200]
    cmp rax, 0
    je L2
    lea rdi, [rip + str9]
    xor eax, eax
    call printf
    jmp L3
L2:
    lea rdi, [rip + str10]
    xor eax, eax
    call printf
L3:
L1:
    mov rax, [rbp - 8]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 208], rax
    mov rax, [rbp - 208]
    cmp rax, 0
    je L4
    mov rax, [rbp - 16]
    cmp rax, 0
    setg al
    movzx rax, al
    mov [rbp - 216], rax
    mov rax, [rbp - 216]
    cmp rax, 0
    je L4
    lea rdi, [rip + str11]
    xor eax, eax
    call printf
L4:
    mov rax, [rbp - 8]
    cmp rax, 0
    setl al
    movzx rax, al
    mov [rbp - 104], rax
    mov rax, [rbp - 104]
    cmp rax, 0
    jne L6
    mov rax, [rbp - 16]
    cmp rax, 0
    setl al
    movzx rax, al
    mov [rbp - 112], rax
    mov rax, [rbp - 112]
    cmp rax, 0
    je L5
L6:
    lea rdi, [rip + str12]
    xor eax, eax
    call printf
L5:
    lea rdi, [rip + str13]
    xor eax, eax
    call printf
    mov rax, 0
    mov [rbp - 56], rax
L7:
    mov rax, [rbp - 56]
    cmp rax, 5
    setl al
    movzx rax, al
    mov [rbp - 120], rax
    mov rax, [rbp - 120]
    cmp rax, 0
    je L8
    lea rdi, [rip + str14]
    mov rsi, [rbp - 56]
    xor eax, eax
    call printf
    mov rax, [rbp - 56]
    add rax, 1
    mov [rbp - 128], rax
    mov rax, [rbp - 128]
    mov [rbp - 56], rax
    jmp L7
L8:
    lea rdi, [rip + str15]
    xor eax, eax
    call printf
    lea rdi, [rip + str16]
    xor eax, eax
    call printf
    mov rax, 10
    mov [rbp - 56], rax
L9:
    mov rax, [rbp - 56]
    cmp rax, 1
    setge al
    movzx rax, al
    mov [rbp - 136], rax
    mov rax, [rbp - 136]
    cmp rax, 0
    je L10
    lea rdi, [rip + str17]
    mov rsi, [rbp - 56]
    xor eax, eax
    call printf
    mov rax, [rbp - 56]
    sub rax, 1
    mov [rbp - 144], rax
    mov rax, [rbp - 144]
    mov [rbp - 56], rax
    jmp L9
L10:
    lea rdi, [rip + str18]
    xor eax, eax
    call printf
    movss xmm0, [rip + __float0]
    movss [rbp - 32], xmm0
    movss xmm0, [rip + __float1]
    movss [rbp - 40], xmm0
    movss xmm0, [rbp - 32]
    mulss xmm0, [rbp - 40]
    movss [rbp - 152], xmm0
    movss xmm0, [rbp - 152]
    movss [rbp - 48], xmm0
    lea rdi, [rip + str19]
    xor eax, eax
    call printf
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
