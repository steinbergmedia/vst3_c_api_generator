#pragma once

#include "types.h"

namespace Steinberg {
namespace Vst {

enum MediaTypes
{
	kAudio = 0,
	kEvent,
	kNumMediaTypes
};

struct IContextMenuItem
{
};

class IContextMenu : public FUnknown
{
public:
	typedef IContextMenuItem Item;
	typedef kEvent ItemEvent;

	static const FUID iid;
};

DECLARE_CLASS_IID (IContextMenu, 0x2E93C863, 0x0C9C4588, 0x97DBECF5, 0xAD17817D)

}}
