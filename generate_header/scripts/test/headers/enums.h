namespace Steinberg {

class IBStream
{
	enum IStreamSeekMode
	{
		kIBSeekSet = 0,
		kIBSeekCur,
		kIBSeekEnd
	};

	enum
	{
		kURLSize = 256,
		kEmailSize = 128,
		kNameSize = 64
	};
};

namespace Vst {

enum MediaTypes
{
	kAudio = 0,
	kEvent,
	kNumMediaTypes
};

class IAutomationState
{
	enum AutomationStates
	{
		kNoAutomation = 0,
		kReadState = 1 << 0,
		kWriteState = 1 << 1,

		kReadWriteState = kReadState | kWriteState,
	};
};

}}
