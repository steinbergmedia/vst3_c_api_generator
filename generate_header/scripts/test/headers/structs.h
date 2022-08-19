#pragma once

#include "types.h"

namespace Steinberg {

struct PFactoryInfo
{
 	enum
	{
		kURLSize = 256,
		kEmailSize = kURLSize << 4,
		kNameSize = kEmailSize >> 3
	};

	char8 vendor[kNameSize | 1];
	char8 url[kURLSize];
	char8 email[kEmailSize];
	int32 flags;
	TUID cid;
};

}
