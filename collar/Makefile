# makefile for dognetd

INCLUDE_DIR:=-I./microhttpd -I./inc -I./sqlite
LIBS:=-lmicrohttpd -lsqlite3
LIBS_DIR:=-L/usr/local/lib
OBJ_DIR:=./obj
SRC_DIR:=./src

BINARY_NAME:=dognetd
OBJ_FILES:=$(OBJ_DIR)/main.o $(OBJ_DIR)/CommandServer.o $(OBJ_DIR)/DogDatabase.o $(OBJ_DIR)/CConvertors.o

dognetd: $(OBJ_DIR) $(OBJ_FILES)
	g++ $(LDFLAGS) $(OBJ_FILES) -o $(BINARY_NAME) $(INCLUDE_DIR) $(LIBS_DIR) $(LIBS)
$(OBJ_DIR):
	mkdir $(OBJ_DIR)
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	g++ $(LDFLAGS) $(INCLUDE_DIR) -c $< -o $@
clean:
	rm $(OBJ_DIR)/*.o $(BINARY_NAME)
