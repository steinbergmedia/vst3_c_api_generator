//------------------------------------------------------------------------
// Flags       : clang-format SMTGSequencer
// Project     : <#Project#>
// Filename    : <#FileName#>
// Created by  : nzorn, 07/2022
// Description : <#Description#>
//------------------------------------------------------------------------

#include <stdint.h>
typedef int32_t Vst_ParamID;

#include "memory.h"
#include "stdlib.h"
#include "string.h"
#include "test_header.h"

int compare_iid (const Steinberg_TUID id1, const Steinberg_TUID id2)
{
	return memcmp (id1, id2, sizeof (Steinberg_TUID)) == 0;
}

static const Steinberg_TUID audioProcessorUID =
    SMTG_INLINE_UID (0xD87D8E9C, 0xE4514B02, 0xB9FCF354, 0xFAC9219C);

static const Steinberg_TUID editControllerUID =
    SMTG_INLINE_UID (0xBACB8EB9, 0xAFAD4C09, 0x90D5893E, 0xCE6D94AD);

struct MyAGainAudioProcessorVtbl
{
	Steinberg_Vst_IComponentVtbl component;
	Steinberg_Vst_IConnectionPointVtbl connectionPoint;
	Steinberg_Vst_IAudioProcessorVtbl audioProcessor;
};

typedef struct
{
	const struct Steinberg_Vst_IComponentVtbl* componentVtbl;
	const struct Steinberg_Vst_IConnectionPointVtbl* connectionPointVtbl;
	const struct Steinberg_Vst_IAudioProcessorVtbl* audioProcessorVtbl;
	Steinberg_int32 refCount;
	struct Steinberg_Vst_IConnectionPoint* connectionPoint;
} MyAGainAudioProcessor;

struct MyAGainEditControllerVtbl
{
	Steinberg_Vst_IEditControllerVtbl editController;
	Steinberg_Vst_IConnectionPointVtbl connectionPoint;
	Steinberg_Vst_IEditController2Vtbl editController2;
};

typedef struct
{
	const struct Steinberg_Vst_IEditControllerVtbl* editControllerVtbl;
	const struct Steinberg_Vst_IConnectionPointVtbl* connectionPointVtbl;
	const struct Steinberg_Vst_IEditController2Vtbl* editController2Vtbl;
	Steinberg_int32 refCount;
} MyAGainEditController;

/*-----------------------------------------------------------------------------------------------------------------------------
Audio Processor Methods*/

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRef (void* thisInterface)
{
	MyAGainAudioProcessor* instance = (MyAGainAudioProcessor*)thisInterface;
	instance->refCount += 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRefConnectionPoint (void* thisInterface)
{
	return AGainProcessor_AddRef ((int64_t)thisInterface - 8);
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRefAudioProcessor (void* thisInterface)
{
	return AGainProcessor_AddRef ((int64_t)thisInterface - 16);
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_Release (void* thisInterface)
{
	MyAGainAudioProcessor* instance = (MyAGainAudioProcessor*)thisInterface;
	if (instance->refCount == 1)
	{
		free (instance);
		return 0;
	}
	instance->refCount -= 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_ReleaseConnectionPoint (void* thisInterface)
{
	return AGainProcessor_Release ((int64_t)thisInterface - 8);
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_ReleaseAudioProcessor (void* thisInterface)
{
	return AGainProcessor_Release ((int64_t)thisInterface - 16);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterface (void* thisInterface,
                                                                        const Steinberg_TUID iid,
                                                                        void** obj)
{
	MyAGainAudioProcessor* instance = (MyAGainAudioProcessor*)thisInterface;
	if (compare_iid (Steinberg_FUnknown_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_IPluginBase_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IComponent_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IConnectionPoint_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + 8);
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IAudioProcessor_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + 16);
		return Steinberg_kResultTrue;
	}
	return Steinberg_kResultFalse;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterfaceConnectionPoint (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainProcessor_QueryInterface ((int64_t)thisInterface - 8, iid, obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterfaceAudioProcessor (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainProcessor_QueryInterface ((int64_t)thisInterface - 16, iid, obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Initialize (void* thisInterface, struct Steinberg_FUnknown* context)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_Terminate (void* thisInterface)
{
	return Steinberg_kNotImplemented;
};

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Connect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	MyAGainAudioProcessor* instance = (MyAGainAudioProcessor*)(int64_t)thisInterface - 8;
	instance->connectionPoint = other;
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Disconnect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	MyAGainAudioProcessor* instance = (MyAGainAudioProcessor*)(int64_t)thisInterface - 8;
	instance->connectionPoint = NULL;
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Notify (void* thisInterface, struct Steinberg_Vst_IMessage* message)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_GetControllerClassId (void* thisInterface, Steinberg_TUID classId)
{
	memcpy (classId, editControllerUID, sizeof (Steinberg_TUID));
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetIoMode (void* thisInterface,
                                                                   Steinberg_Vst_IoMode mode)
{
	return Steinberg_kNotImplemented;
};

Steinberg_int32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetBusCount (void* thisInterface,
                                                                   Steinberg_Vst_MediaType type,
                                                                   Steinberg_Vst_BusDirection dir)
{
	return 0;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_GetBusInfo (
    void* thisInterface, Steinberg_Vst_MediaType type, Steinberg_Vst_BusDirection dir,
    Steinberg_int32 index, struct Steinberg_Vst_BusInfo* bus)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_GetRoutingInfo (void* thisInterface, struct Steinberg_Vst_RoutingInfo* inInfo,
                               struct Steinberg_Vst_RoutingInfo* outInfo)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_ActivateBus (void* thisInterface,
                                                                     Steinberg_Vst_MediaType type,
                                                                     Steinberg_Vst_BusDirection dir,
                                                                     Steinberg_int32 index,
                                                                     Steinberg_TBool state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetActive (void* thisInterface,
                                                                   Steinberg_TBool state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetState (void* thisInterface,
                                                                  struct Steinberg_IBStream* state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_GetState (void* thisInterface,
                                                                  struct Steinberg_IBStream* state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetBusArrangements (
    void* thisInterface, Steinberg_Vst_SpeakerArrangement* inputs, Steinberg_int32 numIns,
    Steinberg_Vst_SpeakerArrangement* outputs, Steinberg_int32 numOuts)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_GetBusArrangement (void* thisInterface, Steinberg_Vst_BusDirection dir,
                                  Steinberg_int32 index, Steinberg_Vst_SpeakerArrangement* arr)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_CanProcessSampleSize (void* thisInterface, Steinberg_int32 symbolicSampleSize)
{
	return Steinberg_kNotImplemented;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetLatencySamples (void* thisInterface)
{
	return 0;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_SetupProcessing (void* thisInterface, struct Steinberg_Vst_ProcessSetup* setup)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetProcessing (void* thisInterface,
                                                                       Steinberg_TBool state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Process (void* thisInterface, struct Steinberg_Vst_ProcessData* data)
{
	return Steinberg_kNotImplemented;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetTailSamples (void* thisInterface)
{
	return 0;
}

/*-----------------------------------------------------------------------------------------------------------------------------
Edit Controller methods*/

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_AddRef (void* thisInterface)
{
	MyAGainEditController* instance = (MyAGainEditController*)thisInterface;
	instance->refCount += 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_Release (void* thisInterface)
{
	MyAGainEditController* instance = (MyAGainEditController*)thisInterface;
	if (instance->refCount == 1)
	{
		free (instance);
		return 0;
	}
	instance->refCount -= 1;
	return instance->refCount;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_QueryInterface (void* thisInterface,
                                                                         const Steinberg_TUID iid,
                                                                         void** obj)
{
	MyAGainEditController* instance = (MyAGainEditController*)thisInterface;
	if (compare_iid (Steinberg_FUnknown_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_IPluginBase_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IEditController_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IConnectionPoint_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + 8);
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IEditController2_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + 16);
		return Steinberg_kResultTrue;
	}
	return Steinberg_kNoInterface;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_Initialize (void* thisInterface, struct Steinberg_FUnknown* context)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_Terminate (void* thisInterface)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_Connect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_Disconnect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_Notify (void* thisInterface, struct Steinberg_Vst_IMessage* message)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_SetComponentState (void* thisInterface, struct Steinberg_IBStream* state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_SetState (void* thisInterface,
                                                                   struct Steinberg_IBStream* state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetState (void* thisInterface,
                                                                   struct Steinberg_IBStream* state)
{
	return Steinberg_kNotImplemented;
}

Steinberg_int32 SMTG_STDMETHODCALLTYPE AGainController_GetParameterCount (void* thisInterface)
{
	return 0;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParameterInfo (
    void* thisInterface, Steinberg_int32 paramIndex, struct Steinberg_Vst_ParameterInfo* info)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParamStringByValue (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue valueNormalized,
    Steinberg_Vst_String128 string)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParamValueByString (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_TChar* string,
    Steinberg_Vst_ParamValue* valueNormalized)
{
	return Steinberg_kNotImplemented;
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE AGainController_NormalizedParamToPlain (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue valueNormalized)
{
	return 0.;
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE AGainController_PlainParamToNormalized (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue plainValue)
{
	return 0.;
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE
AGainController_GetParamNormalized (void* thisInterface, Steinberg_Vst_ParamID id)
{
	return 0.;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_SetParamNormalized (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue value)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_SetComponentHandler (
    void* thisInterface, struct Steinberg_Vst_IComponentHandler* handler)
{
	return Steinberg_kNotImplemented;
}

struct Steinberg_IPlugView* SMTG_STDMETHODCALLTYPE
AGainController_CreateView (void* thisInterface, Steinberg_FIDString name)
{
	return NULL;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_SetKnobMode (void* thisInterface,
                                                                      Steinberg_Vst_KnobMode mode)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_OpenHelp (void* thisInterface,
                                                                   Steinberg_TBool onlyCheck)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_PpenAboutBox (void* thisInterface,
                                                                       Steinberg_TBool onlyCheck)
{
	return Steinberg_kNotImplemented;
}

static const struct MyAGainAudioProcessorVtbl myAGainAudioProcessorVtbl = {
    {AGainProcessor_QueryInterface, AGainProcessor_AddRef, AGainProcessor_Release,
     AGainProcessor_Initialize, AGainProcessor_Terminate, AGainProcessor_GetControllerClassId,
     AGainProcessor_SetIoMode, AGainProcessor_GetBusCount, AGainProcessor_GetBusInfo,
     AGainProcessor_GetRoutingInfo, AGainProcessor_ActivateBus, AGainProcessor_SetActive,
     AGainProcessor_SetState, AGainProcessor_GetState},
    {AGainProcessor_QueryInterfaceConnectionPoint, AGainProcessor_AddRefConnectionPoint,
     AGainProcessor_ReleaseConnectionPoint, AGainProcessor_Connect, AGainProcessor_Disconnect,
     AGainProcessor_Notify},
    {AGainProcessor_QueryInterfaceAudioProcessor, AGainProcessor_AddRefAudioProcessor,
     AGainProcessor_ReleaseAudioProcessor, AGainProcessor_SetBusArrangements,
     AGainProcessor_GetBusArrangement, AGainProcessor_CanProcessSampleSize,
     AGainProcessor_GetLatencySamples, AGainProcessor_SetupProcessing, AGainProcessor_SetProcessing,
     AGainProcessor_Process, AGainProcessor_GetTailSamples},
};

static const struct MyAGainEditControllerVtbl myAGainEditControllerVtbl = {
    {AGainController_QueryInterface, AGainController_AddRef, AGainController_Release,
     AGainController_Initialize, AGainController_Terminate, AGainController_SetComponentState,
     AGainController_SetState, AGainController_GetState, AGainController_GetParameterCount,
     AGainController_GetParameterInfo, AGainController_GetParamStringByValue,
     AGainController_GetParamValueByString, AGainController_NormalizedParamToPlain,
     AGainController_PlainParamToNormalized, AGainController_GetParamNormalized,
     AGainController_SetParamNormalized, AGainController_SetComponentHandler,
     AGainController_CreateView},
    {AGainController_QueryInterface, AGainController_AddRef, AGainController_Release,
     AGainController_Connect, AGainController_Disconnect, AGainController_Notify},
    {AGainController_QueryInterface, AGainController_AddRef, AGainController_Release,
     AGainController_SetKnobMode, AGainController_OpenHelp, AGainController_PpenAboutBox}};

/* methods derived from "Steinberg_FUnknown": */
Steinberg_uint32 SMTG_STDMETHODCALLTYPE myAddRef (void* thisInterface)
{
	return 100;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE myRelease (void* thisInterface)
{
	return 100;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE myQueryInterface (void* thisInterface,
                                                           const Steinberg_TUID iid, void** obj)
{
	if (compare_iid (iid, Steinberg_FUnknown_iid))
	{
		myAddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (iid, Steinberg_IPluginFactory_iid))
	{
		myAddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (iid, Steinberg_IPluginFactory2_iid))
	{
		myAddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	return Steinberg_kNoInterface;
}

/* methods derived from "Steinberg_IPluginFactory": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetFactoryInfo (void* thisInterface,
                                                           struct Steinberg_PFactoryInfo* info)
{
	if (info == 0)
	{
		return Steinberg_kInvalidArgument;
	}
	strcpy (info->vendor, "test_vendor");
	strcpy (info->email, "test_email");
	strcpy (info->url, "test_url");
	info->flags = 16;
	return Steinberg_kResultTrue;
}

Steinberg_int32 SMTG_STDMETHODCALLTYPE myCountClasses (void* thisInterface)
{
	return 2;
}

static struct Steinberg_PClassInfo2 classes[2];

Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetClassInfo (void* thisInterface, Steinberg_int32 index,
                                                         struct Steinberg_PClassInfo* info)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE myCreateInstance (void* thisInterface,
                                                           Steinberg_FIDString cid,
                                                           Steinberg_FIDString iid, void** obj)
{
	if (compare_iid (Steinberg_Vst_IComponent_iid, iid) && compare_iid (cid, classes[0].cid))
	{
		MyAGainAudioProcessor* instance =
		    (MyAGainAudioProcessor*)malloc (sizeof (MyAGainAudioProcessor));
		instance->componentVtbl = &myAGainAudioProcessorVtbl.component;
		instance->connectionPointVtbl = &myAGainAudioProcessorVtbl.connectionPoint;
		instance->audioProcessorVtbl = &myAGainAudioProcessorVtbl.audioProcessor;
		instance->refCount = 1;
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IEditController_iid, iid) && compare_iid (cid, classes[1].cid))
	{
		MyAGainEditController* instance =
		    (MyAGainEditController*)malloc (sizeof (MyAGainEditController));
		instance->editControllerVtbl = &myAGainEditControllerVtbl.editController;
		instance->connectionPointVtbl = &myAGainEditControllerVtbl.connectionPoint;
		instance->editController2Vtbl = &myAGainEditControllerVtbl.editController2;
		instance->refCount = 1;
		*obj = instance;
		return Steinberg_kResultTrue;
	}
	return Steinberg_kResultFalse;
}

/* methods defined in "Steinberg_IPluginFactory2": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetClassInfo2 (void* thisInterface,
                                                          Steinberg_int32 index,
                                                          struct Steinberg_PClassInfo2* info)
{
	if (index > 1 || info == 0)
	{
		return Steinberg_kInvalidArgument;
	}
	memcpy (info, &classes[index], sizeof (struct Steinberg_PClassInfo2));
	return Steinberg_kResultTrue;
}

static const Steinberg_IPluginFactory2Vtbl myPluginFactoryVtbl = {
    myQueryInterface, myAddRef,       myRelease,        myGetFactoryInfo,
    myCountClasses,   myGetClassInfo, myCreateInstance, myGetClassInfo2};

static Steinberg_IPluginFactory2 myPluginFactory = {&myPluginFactoryVtbl};

#if __APPLE__
#define SMTG_EXPORT_SYMBOL __attribute__ ((visibility ("default")))
#else
#define SMTG_EXPORT_SYMBOL __declspec (dllexport)
#endif

SMTG_EXPORT_SYMBOL Steinberg_IPluginFactory* SMTG_STDMETHODCALLTYPE GetPluginFactory ()
{
	memcpy (classes[0].cid, audioProcessorUID, sizeof (Steinberg_TUID));
	classes[0].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
	strcpy (classes[0].category, "Audio Module Class");
	static const Steinberg_char16 name[] = {'A', 'G', 'A', 'I', 'N'};
	memcpy (classes[0].name, name, sizeof (name));
	classes[0].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
	strcpy (classes[0].subCategories, "Fx");
	classes[0].vendor[0] = 0;
	classes[0].version[0] = 0;
	classes[0].sdkVersion[0] = 0;

	memcpy (classes[1].cid, editControllerUID, sizeof (Steinberg_TUID));
	classes[1].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
	strcpy (classes[1].category, "Component Controller Class");
	static const Steinberg_char16 name2[] = {'A', 'G', 'A', 'I', 'N'};
	memcpy (classes[1].name, name2, sizeof (name2));
	classes[1].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
	strcpy (classes[1].subCategories, "Fx");
	classes[1].vendor[0] = 0;
	classes[1].version[0] = 0;
	classes[1].sdkVersion[0] = 0;

	return (Steinberg_IPluginFactory*)&myPluginFactory;
}

#if __APPLE__
SMTG_EXPORT_SYMBOL Steinberg_TBool bundleEntry (void* bundleRef)
{
	return 1;
}
SMTG_EXPORT_SYMBOL Steinberg_TBool bundleExit (void* bundleRef)
{
	return 1;
}
#endif
