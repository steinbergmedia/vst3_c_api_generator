typedef enum
{
    Steinberg_IBStream_IStreamSeekMode_kIBSeekSet = 0,
    Steinberg_IBStream_IStreamSeekMode_kIBSeekCur,
    Steinberg_IBStream_IStreamSeekMode_kIBSeekEnd
} Steinberg_IBStream_IStreamSeekMode;

typedef enum
{
    Steinberg_Vst_MediaTypes_kAudio = 0,
    Steinberg_Vst_MediaTypes_kEvent,
    Steinberg_Vst_MediaTypes_kNumMediaTypes
} Steinberg_Vst_MediaTypes;

typedef enum
{
    Steinberg_Vst_IAutomationState_AutomationStates_kNoAutomation = 0,
    Steinberg_Vst_IAutomationState_AutomationStates_kReadState = 1 << 0,
    Steinberg_Vst_IAutomationState_AutomationStates_kWriteState = 1 << 1,
    Steinberg_Vst_IAutomationState_AutomationStates_kReadWriteState = Steinberg_Vst_IAutomationState_AutomationStates_kReadState | Steinberg_Vst_IAutomationState_AutomationStates_kWriteState
} Steinberg_Vst_IAutomationState_AutomationStates;