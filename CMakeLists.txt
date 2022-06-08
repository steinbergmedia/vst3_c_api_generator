cmake_minimum_required(VERSION 3.15.0)

include(FetchContent)

FetchContent_Declare(
pluginterfaces
GIT_REPOSITORY https://stash.steinberg-intra.net/scm/vstsdk/vst3_pluginterfaces.git
GIT_TAG v3.7.5_build_44
)
FetchContent_GetProperties(pluginterfaces)
if(NOT pluginterfaces_POPULATED)
  # Fetch the content using previously declared details
  FetchContent_Populate(pluginterfaces)
endif()

find_package (Python3)
#execute_process(COMMAND "${Python3_EXECUTABLE}" interface_convert.py header_compilation.h)

project(GeneratorTest)
add_executable(GeneratorTest main.cpp)

add_custom_command(TARGET GeneratorTest
                    PRE_BUILD
                    COMMAND "${Python3_EXECUTABLE}" ${CMAKE_CURRENT_SOURCE_DIR}/interface_convert.py header_compilation.h
                    )

