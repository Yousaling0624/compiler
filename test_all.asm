section .data
    str0 db "Enter a: ", 0
    str1 db "%d", 0
    str10 db "a == b\n", 0
    str11 db "Both positive\n", 0
    str12 db "At least one negative\n", 0
    str13 db "While loop: ", 0
    str14 db "%d ", 0
    str15 db "\n", 0
    str16 db "For loop: ", 0
    str17 db "%d ", 0
    str18 db "\n", 0
    str19 db "Float computation done.\n", 0
    str2 db "Enter b: ", 0
    str3 db "%d", 0
    str4 db "Sum: %d\n", 0
    str5 db "Product: %d\n", 0
    str6 db "Division: %d\n", 0
    str7 db "Modulo: %d\n", 0
    str8 db "a > b\n", 0
    str9 db "a < b\n", 0
    __float0 dd 1069547520
    __float1 dd 1075838976

section .text
    extern printf, scanf

global main
main:
    push rbp
    mov rbp, rsp
    sub rsp, 232
    lea rdi, [str0]
    xor eax, eax
    call printf
    lea rax, [rbp - 8]
    mov [rbp - 88], rax
    lea rdi, [str1]
    mov rsi, [rbp - 88]
    xor eax, eax
    call scanf
    lea rdi, [str2]
    xor eax, eax
    call printf
    lea rax, [rbp - 16]
    mov [rbp - 96], rax
    lea rdi, [str3]
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
    lea rdi, [str4]
    mov rsi, [rbp - 80]
    xor eax, eax
    call printf
    lea rdi, [str5]
    mov rsi, [rbp - 72]
    xor eax, eax
    call printf
    lea rdi, [str6]
    mov rsi, [rbp - 24]
    xor eax, eax
    call printf
    lea rdi, [str7]
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
    lea rdi, [str8]
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
    lea rdi, [str9]
    xor eax, eax
    call printf
    jmp L3
L2:
    lea rdi, [str10]
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
    lea rdi, [str11]
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
    lea rdi, [str12]
    xor eax, eax
    call printf
L5:
    lea rdi, [str13]
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
    lea rdi, [str14]
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
    lea rdi, [str15]
    xor eax, eax
    call printf
    lea rdi, [str16]
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
    lea rdi, [str17]
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
    lea rdi, [str18]
    xor eax, eax
    call printf
    movss xmm0, [rel __float0]
    movss [rbp - 32], xmm0
    movss xmm0, [rel __float1]
    movss [rbp - 40], xmm0
    movss xmm0, [rbp - 32]
    mulss xmm0, [rbp - 40]
    movss [rbp - 152], xmm0
    movss xmm0, [rbp - 152]
    movss [rbp - 48], xmm0
    lea rdi, [str19]
    xor eax, eax
    call printf
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret
