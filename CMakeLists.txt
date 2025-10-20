cmake_minimum_required(VERSION 3.15.0)

###############################################################################################
## Default Options
###############################################################################################

set(SMTG_PLUGINTERFACES_REPO_TYPE_DEFAULT git)
set(SMTG_PLUGINTERFACES_REPO_DEFAULT https://github.com/steinbergmedia/vst3_pluginterfaces.git)
set(SMTG_PLUGINTERFACES_GIT_TAG_DEFAULT HEAD)

###############################################################################################
## Options
###############################################################################################

set(SMTG_PLUGINTERFACES_REPO_TYPE
	${SMTG_PLUGINTERFACES_REPO_TYPE_DEFAULT}
	CACHE STRING "The VST3 pluginterfaces (API) repository type (git or file)"
)
set(SMTG_PLUGINTERFACES_REPO
	${SMTG_PLUGINTERFACES_REPO_DEFAULT}
	CACHE STRING "The VST3 pluginterfaces (API) repository"
)
set(SMTG_PLUGINTERFACES_GIT_TAG
	${SMTG_PLUGINTERFACES_GIT_TAG_DEFAULT}
	CACHE STRING "The VST3 pluginterfaces (API) git tag"
)

###############################################################################################
## Fetch the VST API repository
###############################################################################################

if(${SMTG_PLUGINTERFACES_REPO_TYPE} STREQUAL git)
	include(FetchContent)

	FetchContent_Declare(
		pluginterfaces
		GIT_REPOSITORY		${SMTG_PLUGINTERFACES_REPO}
		GIT_TAG				${SMTG_PLUGINTERFACES_GIT_TAG}
		GIT_SHALLOW			TRUE
		GIT_PROGRESS		TRUE
		SOURCE_DIR			"${CMAKE_BINARY_DIR}/_deps/pluginterfaces"
	)
	message(STATUS "Git clone pluginterfaces")
	FetchContent_Populate(pluginterfaces)
	message(STATUS "Git clone pluginterfaces done.")

elseif(${SMTG_PLUGINTERFACES_REPO_TYPE} STREQUAL file)
	execute_process(COMMAND /bin/rm -rf "${CMAKE_BINARY_DIR}/_deps/pluginterfaces")
	execute_process(COMMAND /bin/mkdir -p "${CMAKE_BINARY_DIR}/_deps")
	execute_process(COMMAND /bin/cp -R ${SMTG_PLUGINTERFACES_REPO} "${CMAKE_BINARY_DIR}/_deps/pluginterfaces")
	set(pluginterfaces_SOURCE_DIR ${CMAKE_BINARY_DIR}/_deps/pluginterfaces)
else()
	message(FATAL_ERROR "Wrong repo type")
endif()

###############################################################################################
## Prepare Python
###############################################################################################
find_package (Python3)

set(venv_dir ${CMAKE_BINARY_DIR}/venv)
message(STATUS "Execute: ${Python3_EXECUTABLE} -m venv ${venv_dir}")
execute_process(COMMAND ${Python3_EXECUTABLE} -m venv ${venv_dir})
if(APPLE)
	set(venv_python_exe ${venv_dir}/bin/python)
elseif(WIN32)
	set(venv_python_exe ${venv_dir}/Scripts/python.exe)
endif()

message(STATUS "Execute: ${venv_python_exe} -m pip install --upgrade pip")
execute_process(COMMAND ${venv_python_exe} -m pip install --upgrade pip)

foreach(library libclang==18.1.* clang==18.1.* jinja2)
	message(STATUS "Execute: ${venv_python_exe} -m pip install ${library}")
	execute_process(COMMAND ${venv_python_exe} -m pip install ${library})
endforeach()

###############################################################################################
## Project
###############################################################################################

project(
	VST3_C_API_GENERATOR
	VERSION 1.0.0
)

###############################################################################################
## Generate Interface Target
###############################################################################################

add_executable(Generate_Header generate_header/generate_header.c generate_header/scripts)
target_include_directories(Generate_Header PRIVATE ${CMAKE_BINARY_DIR})

if(APPLE)
    execute_process(OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE CMAKE_OSX_SYSROOT COMMAND /usr/bin/xcrun --show-sdk-path)
    set(sysroot_arg "-isysroot;${CMAKE_OSX_SYSROOT}")
endif()

add_custom_command(
    TARGET Generate_Header
    PRE_BUILD
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E echo "${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/generate_header_compilation.py ${pluginterfaces_SOURCE_DIR}"
    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/generate_header_compilation.py ${pluginterfaces_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} -E echo "${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/interface_convert.py ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h '${sysroot_arg}'"
    COMMAND ${venv_python_exe} ${CMAKE_CURRENT_SOURCE_DIR}/generate_header/scripts/interface_convert.py ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h ${sysroot_arg}
)
add_custom_command(
    TARGET Generate_Header
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E rm -f ${CMAKE_BINARY_DIR}/_deps/pluginterfaces/vst/header_compilation.h
)

###############################################################################################
## Validate Interface Target
###############################################################################################

add_executable(Validate_Interfaces 
	validate_interfaces/main.c
	validate_interfaces/test2.c
	validate_interfaces/cxx.cpp
	"${CMAKE_BINARY_DIR}/_deps/pluginterfaces"
)
target_include_directories(Validate_Interfaces PRIVATE "${CMAKE_BINARY_DIR}" "${pluginterfaces_SOURCE_DIR}/..")
target_compile_features(Validate_Interfaces
    PUBLIC
        cxx_std_17
)
add_dependencies(Validate_Interfaces Generate_Header)

###############################################################################################
## CGain Target
###############################################################################################

add_library(C_Gain_Test MODULE c_gain_test_plugin/cgain.c)
target_include_directories(C_Gain_Test PRIVATE ${CMAKE_BINARY_DIR})

if(APPLE)
	set_target_properties(C_Gain_Test
		PROPERTIES
			BUNDLE TRUE
			XCODE_ATTRIBUTE_GENERATE_PKGINFO_FILE YES
			XCODE_ATTRIBUTE_WRAPPER_EXTENSION vst3
	)
else()
    set_target_properties(C_Gain_Test
        PROPERTIES
            SUFFIX ".vst3")
endif()

add_dependencies(C_Gain_Test Validate_Interfaces)
