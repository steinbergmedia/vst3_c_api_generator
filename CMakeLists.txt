cmake_minimum_required(VERSION 3.15.0)

include(FetchContent)

FetchContent_Declare(
pluginterfaces
GIT_REPOSITORY https://stash.steinberg-intra.net/scm/vstsdk/vst3_pluginterfaces.git
GIT_TAG v3.7.5_build_44
SOURCE_DIR "${CMAKE_BINARY_DIR}/_deps/pluginterfaces"
)
FetchContent_GetProperties(pluginterfaces)
if(NOT pluginterfaces_POPULATED)
  # Fetch the content using previously declared details
  FetchContent_Populate(pluginterfaces)
endif()

find_package (Python3)

project(GeneratorTest)
add_executable(GeneratorTest main.c)
target_include_directories(GeneratorTest PRIVATE ${CMAKE_BINARY_DIR})

set(venv_dir ${CMAKE_CURRENT_SOURCE_DIR}/build/venv)
execute_process(COMMAND ${Python3_EXECUTABLE} -m venv ${venv_dir})
if(APPLE)
  set(venv_python_exe ${venv_dir}/bin/python)
elseif(WIN32)
  set(venv_python_exe ${venv_dir}/Scripts/python.exe)
endif()

execute_process(COMMAND ${venv_python_exe} -m pip install --upgrade pip)

foreach(library libclang clang jinja2)
  execute_process(COMMAND ${venv_python_exe} -m pip install ${library})
endforeach()

add_custom_command(TARGET GeneratorTest
                    PRE_BUILD
                    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
                    COMMAND ${CMAKE_COMMAND} -E rm -f ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
                    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header_compilation.py ${pluginterfaces_SOURCE_DIR}
                    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/interface_convert.py ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
                    )
#add_custom_command(TARGET GeneratorTest
#                    POST_BUILD
#                    COMMAND ${CMAKE_COMMAND} -E rm -f ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
#                    )
