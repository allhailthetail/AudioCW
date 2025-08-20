# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++20

# Library flags
AudioCW_LIBS = -lsndfile -lm

# Source files
AudioCW_SRC = src/AudioCW/main.cpp
GUI_SRC = src/gui.py

# Object files
AudioCW_OBJ = build/audiocw.o  # Change to just the object file in build/

# Install Prefix
INSTALL_PREFIX = /usr

# Executable name
AudioCW_TARGET = build/audiocw
GUI_TARGET = build/audiocw-gui

# Default target
all: $(AudioCW_TARGET) $(GUI_TARGET)

# Target for audiocw
$(AudioCW_TARGET): $(AudioCW_OBJ)
	mkdir -p build/
	$(CXX) $(CXXFLAGS) -o $@ $^ $(AudioCW_LIBS)
$(AudioCW_OBJ): $(AudioCW_SRC)
	mkdir -p build/
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Target for audiocw-gui
$(GUI_TARGET): $(GUI_SRC)
	mkdir -p build/
	echo "#!/usr/bin/python3" > $@
	cat $(GUI_SRC) >> $@
	chmod +x $@

# Target for install
install:
	sudo cp $(AudioCW_TARGET) $(GUI_TARGET) $(INSTALL_PREFIX)/local/bin
	sudo cp audiocw-gui.desktop $(INSTALL_PREFIX)/share/applications
	sudo cp img/48/audiocw_48.png $(INSTALL_PREFIX)/share/icons/hicolor/48x48/apps/audiocw-gui.png

# Target for uninstall
uninstall:
	sudo rm $(INSTALL_PREFIX)/local/bin/audiocw
	sudo rm $(INSTALL_PREFIX)/local/bin/audiocw-gui
	sudo rm $(INSTALL_PREFIX)/share/applications/audiocw-gui.desktop
	sudo rm $(INSTALL_PREFIX)/share/icons/hicolor/48x48/apps/audiocw-gui.png

# Clean up build files
clean:
	rm -rf build/
