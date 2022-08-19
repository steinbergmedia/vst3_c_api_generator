namespace Steinberg {

#ifdef UNICODE
	typedef char16 tchar;
#else
	typedef char8 tchar;
#endif

typedef char int8;
typedef char char8;
typedef long int32;
typedef unsigned long uint32;
typedef int32 UCoord;
typedef int32 tresult;
typedef int8 TUID[16];
typedef const char8* FIDString
typedef const tchar* CString;
typedef int32 UnitID;
typedef int32 ProgramListID;

class FUID;
struct PClassInfo2;
struct PClassInfoW;

#define PLUGIN_API

}
