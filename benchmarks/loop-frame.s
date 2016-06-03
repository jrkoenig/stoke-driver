  .text
  .globl inc
  .type inc, @function
.inc:
  nop
  nop
  nop
  nop 
.L_start:       
  nop
  cmpl %edi, %edi
  jne .L_start               
  nop
  retq
.size inc, .-inc
