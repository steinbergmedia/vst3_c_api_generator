#include <stdint.h>
#include <assert.h>
typedef int32_t Vst_ParamID;

#include "test_header.h"


int main ()
{
	assert (sizeof(struct Steinberg_PFactoryInfo) == 452);
	return 0;
}
