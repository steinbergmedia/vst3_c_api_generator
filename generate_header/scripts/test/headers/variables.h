#pragma once

#include "vsttypes.h"

namespace Steinberg {

struct PFactoryInfo
{
	enum FactoryFlags
	{
		kUnicode = 1 << 4
	};
};

namespace Vst {

#define ATTR_STYLE "style"

namespace Attributes
{
	const CString kStyle = ATTR_STYLE;
	static const int32 kMaxInt = INT_MAX;
	static const int32 kMinInt = INT_MIN;
};

static const UnitID kNoParentUnitId = -1;
const Speaker kSpeakerL = 1 << 0;
const Speaker kSpeakerR = 1 << 1;
const Speaker kSpeakerC = 1 << 2;
const Speaker kSpeakerLfe = 1 << 3;
const Speaker kSpeakerLs = 1 << 4;
const Speaker kSpeakerRs = 1 << 5;
const Speaker kSpeakerPl = (Speaker)1 << 31;
const Speaker kSpeakerPr = (Speaker)1 << 32;
const SpeakerArrangement k71Proximity = kSpeakerL | kSpeakerR | kSpeakerC | kSpeakerLfe | kSpeakerLs | kSpeakerRs | kSpeakerPl | kSpeakerPr;
const CString kStringEmpty = "";
const CString kStringStereoR = "Stereo (Ls Rs)";

}

static const int32 kMinLong = (-0x42-1);
static const int32 kMinInt32 = kMinLong;

static const uint32 kMaxInt32u = int32 (kMinInt32) | (int32 (0x42) << 23);
static const UCoord kMinCoord = ((UCoord)-0x42);

const int32 kDefaultFactoryFlags = PFactoryInfo::kUnicode;

}
