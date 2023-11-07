CC=clang
LD=llvm-objcopy
CFLAGS=-Wl,-Ttext=0x0 -nostdlib --target=riscv64 -march=rv64g -mno-relax

run:
	python3 src/pyemu.py test/add-addi.bin

.PHONY: run