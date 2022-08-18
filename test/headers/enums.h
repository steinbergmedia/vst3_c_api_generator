namespace Steinberg {

class IBStream
{
	enum IStreamSeekMode
	{
		kIBSeekSet = 0,
		kIBSeekCur,
		kIBSeekEnd
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
