static const Steinberg_CString Steinberg_Vst_Attributes_kStyle = "style";
static const Steinberg_int32 Steinberg_Vst_Attributes_kMaxInt = INT_MAX;
static const Steinberg_int32 Steinberg_Vst_Attributes_kMinInt = INT_MIN;
static const Steinberg_UnitID Steinberg_Vst_kNoParentUnitId = -1;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerL = 1 << 0;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerR = 1 << 1;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerC = 1 << 2;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerLfe = 1 << 3;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerLs = 1 << 4;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerRs = 1 << 5;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerPl = (Steinberg_Vst_Speaker) 1 << 31;
static const Steinberg_Vst_Speaker Steinberg_Vst_kSpeakerPr = (Steinberg_Vst_Speaker) 1 << 32;
static const Steinberg_Vst_SpeakerArrangement Steinberg_Vst_k71Proximity = 1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 4 | 1 << 5 | (Steinberg_Vst_Speaker) 1 << 31 | (Steinberg_Vst_Speaker) 1 << 32;
static const Steinberg_CString Steinberg_Vst_kStringEmpty = "";
static const Steinberg_CString Steinberg_Vst_kStringStereoR = "Stereo (Ls Rs)";
static const Steinberg_int32 Steinberg_kMinLong = (-0x42 - 1);
static const Steinberg_int32 Steinberg_kMinInt32 = (-0x42 - 1);
static const Steinberg_uint32 Steinberg_kMaxInt32u = (Steinberg_int32) (-0x42 - 1) | ((Steinberg_int32) 0x42 << 23);
static const Steinberg_UCoord Steinberg_kMinCoord = ((Steinberg_UCoord) -0x42);
static const Steinberg_int32 Steinberg_kDefaultFactoryFlags = 1 << 4;