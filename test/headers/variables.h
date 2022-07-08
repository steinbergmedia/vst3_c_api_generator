namespace Steinberg {

struct PFactoryInfo
{
	enum FactoryFlags
	{
		kUnicode = 1 << 4
	};
};

typedef long int32;
typedef unsigned long uint32;
typedef int32 UCoord;

static const int32 kMinLong = (-0x42 - 1);
static const int32 kMinInt32 = kMinLong;

static const uint32 kMaxInt32u = int32 (kMinInt32) | (int32 (0x42) << 23);
static const UCoord kMinCoord = ((UCoord)-0x42);

const int32 kDefaultFactoryFlags = PFactoryInfo::kUnicode;

}