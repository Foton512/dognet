# makefile for dognetd

INCLUDE_DIR:=-I./microhttpd -I./inc -I./sqlite -I./json
LIBS:=-lmicrohttpd -lsqlite3 -lcurl -pthread
LIBS_DIR:=-L/usr/local/lib
OBJ_DIR:=./obj
SRC_DIR:=./src
GPP:=g++-4.7

BINARY_NAME:=dognetd
OBJ_FILES:= \
	$(OBJ_DIR)/main.o \
	$(OBJ_DIR)/CommandServer.o \
	$(OBJ_DIR)/DogDatabase.o \
	$(OBJ_DIR)/CConvertors.o \
	$(OBJ_DIR)/CoordUploader.o \
	$(OBJ_DIR)/CoordsReader.o \
	$(OBJ_DIR)/ArduinoController.o \
	$(OBJ_DIR)/md5.o \
	$(OBJ_DIR)/jsoncpp.o

dognetd: $(OBJ_DIR) $(OBJ_FILES)
	$(GPP) -std=c++11 $(LDFLAGS) $(OBJ_FILES) -o $(BINARY_NAME) $(INCLUDE_DIR) $(LIBS_DIR) $(LIBS)
$(OBJ_DIR):
	mkdir $(OBJ_DIR)
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(GPP) -std=c++11 $(LDFLAGS) $(INCLUDE_DIR) -c $< -o $@
clean:
	rm -f $(OBJ_DIR)/*.o $(BINARY_NAME)
