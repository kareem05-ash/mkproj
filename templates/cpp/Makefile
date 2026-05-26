CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Wpedantic -Iinclude
TARGET   := build/{{project_name}}
SRCS     := $(wildcard src/*.cpp)
OBJS     := $(patsubst src/%.cpp,build/%.o,$(SRCS))

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

build/%.o: src/%.cpp | build
	$(CXX) $(CXXFLAGS) -c -o $@ $<

build:
	mkdir -p build

test:
	@echo "No tests configured yet."

clean:
	rm -rf build/
