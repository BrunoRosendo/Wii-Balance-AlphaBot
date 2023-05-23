CC=gcc
CFLAGS = -Wall
INCLUDES = /usr/include/python3.9/
LIBS = -lpython3.x

SOURCE = kernel.c
SOURCE_OBJ = $(SOURCE:.c=.o)
EXEC = kernel

all: $(EXEC)

%.o: %.c
	$(CC) $(CFLAGS) -I $(INCLUDES) -c $< -o $@

$(EXEC): $(SOURCE_OBJ)
	$(CC) $(CFLAGS) -o $@ $(SOURCE_OBJ) $(LIBS)

clean:
	rm -rf $(EXEC) *.o *.d
