# Makefile for Bach in the Mirror
# Allows standard make workflow and dynamic processor detection:
#   make            -> Builds all inventions using all available processor cores
#   make -j8        -> Overrides job concurrency
#   make 01         -> Builds only Invention 01
#   make clean      -> Wipes intermediate tmp and rendered scores

# Dynamically query available CPU / processor count across Linux (nproc) and macOS/BSD (sysctl / getconf)
NPROCS := $(shell getconf _NPROCESSORS_ONLN 2>/dev/null || nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
JOBS ?= $(NPROCS)

.PHONY: all default clean 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15

# Default target builds with auto-detected parallel jobs
default:
	./build.sh -j $(JOBS)

all:
	./build.sh -j $(JOBS) --all

# Clean temporary files and rendered outputs
clean:
	rm -rf mozart-transpose-output/tmp
	rm -rf mozart-transpose-output/png/*
	rm -rf frontend/png/*
	mkdir -p mozart-transpose-output/tmp mozart-transpose-output/png frontend/png

# Individual invention targets
01 02 03 04 05 06 07 08 09 10 11 12 13 14 15:
	./build.sh -j $(JOBS) $@
