#pragma once

#include "types.h"

namespace Steinberg {

#define INLINE_UID(l1, l2, l3, l4)

#define DECLARE_CLASS_IID(ClassName, l1, l2, l3, l4) \
	static const ::Steinberg::TUID ClassName##_iid = INLINE_UID (l1, l2, l3, l4);

class FUnknown
{
	virtual tresult PLUGIN_API queryInterface (const TUID _iid, void** obj) = 0;

	virtual uint32 PLUGIN_API addRef () = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (FUnknown, 0x00000000, 0x00000000, 0xC0000000, 0x00000046)

}
