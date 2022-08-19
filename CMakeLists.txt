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

project(Convert_Interfaces_To_C)

add_executable(Generate_Header generate_header/generate_header.c)
target_include_directories(Generate_Header PRIVATE ${CMAKE_BINARY_DIR})

add_executable(Validate_Interfaces validate_interfaces/main.c validate_interfaces/test2.c)
target_include_directories(Validate_Interfaces PRIVATE ${CMAKE_BINARY_DIR})

set(venv_dir ${CMAKE_BINARY_DIR}/venv)
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

add_custom_command(TARGET Generate_Header
                    PRE_BUILD
                    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
                    COMMAND ${CMAKE_COMMAND} -E rm -f ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
                    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/generate_header_compilation.py ${pluginterfaces_SOURCE_DIR}
                    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/interface_convert.py ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
                    POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E rm -f ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
                    )

add_library(C_Gain_Example MODULE c_gain_example/factory.c)
target_include_directories(C_Gain_Example PRIVATE ${CMAKE_BINARY_DIR})

if(APPLE)
	set_target_properties(C_Gain_Example
		PROPERTIES
			BUNDLE TRUE
			XCODE_ATTRIBUTE_WRAPPER_EXTENSION vst3
	)
else()
    set_target_properties(C_Gain_Example
        PROPERTIES
            SUFFIX ".vst3")
endif()
