## VST3 C API Generator

This repository contains scripts for generating and testing the C API from the VST3 c++ SDK

---

The `generate_header` folder contains the scripts to create the `vst3_c_api.h` header file

The `validate_interafaces` folder contains c and c++ source files to validate the generated header

The `c_gain_test_plugin` folder contains a simple VST3 Plug-in written in C

---

To build it use cmake:

	mkdir build
	cd build
	cmake ../
	cmake --build .

---

Check the LICENSE.txt for the license
