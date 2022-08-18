#pragma once

#include "funknown.h"
#include "structs.h"

namespace Steinberg {
namespace Vst {

enum MediaTypes
{
	kAudio = 0,
	kEvent,
	kNumMediaTypes
};

struct UnitInfo
{
	UnitID id;
	UnitID parentUnitId;
	CString name;
	ProgramListID programListId;
};

class IUnitHandler : public FUnknown
{
	virtual tresult PLUGIN_API notifyUnitSelection (kEvent event) = 0;
	virtual tresult PLUGIN_API notifyProgramListChange (ProgramListID listId, int32 programIndex) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IUnitHandler, 0x4B5147F8, 0x4654486B, 0x8DAB30BA, 0x163A3C56)

class IUnitHandler2 : public FUnknown
{
	virtual tresult PLUGIN_API notifyUnitByBusChange () = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IUnitHandler2, 0xF89F8CDF, 0x699E4BA5, 0x96AAC9A4, 0x81452B01)

class IUnitInfo : public IUnitHandler2, public IUnitHandler
{
	virtual int32 PLUGIN_API getUnitCount () = 0;
	virtual tresult PLUGIN_API getUnitInfo (int32 unitIndex, UnitInfo& info /*out*/) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IUnitInfo, 0x3D4BD6B5, 0x913A4FD2, 0xA886E768, 0xA5EB92C1)

}}
