cmake_minimum_required(VERSION 3.20)
project(C_Server C)

set(CMAKE_C_STANDARD 99)
link_libraries(-lwsock32)
link_libraries(-lpthread)
file(
        #        GLOB SOURCES src/*.cpp src/*.h
#        GLOB SOURCES Htable.h
        GLOB SOURCES *.c *.h
)
add_executable(C_Server main.c ${SOURCES})
