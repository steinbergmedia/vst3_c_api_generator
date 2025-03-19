//------------------------------------------------------------------------
// Flags       : clang-format SMTGSequencer
// Project     : VST3 C API Generator
// Filename    : cgain.c
// Created by  : nzorn, 07/2022
// Description : Example VST3 Plug-in using the C API
//------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// This file is part of a Steinberg SDK. It is subject to the license terms
// in the LICENSE file found in the top-level directory of this distribution
// and at www.steinberg.net/sdklicenses.
// No part of the SDK, including this file, may be copied, modified, propagated,
// or distributed except according to the terms contained in the LICENSE file.
//-----------------------------------------------------------------------------

#include <math.h>
#include <memory.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vst3_c_api.h"

static size_t pointerOffset = sizeof (void*);

int compare_iid (const Steinberg_TUID id1, const Steinberg_TUID id2)
{
	return memcmp (id1, id2, sizeof (Steinberg_TUID)) == 0;
}

static const Steinberg_TUID audioProcessorUID =
    SMTG_INLINE_UID (0xD87D8E9C, 0xE4514B02, 0xB9FCF354, 0xFAC9219C);

static const Steinberg_TUID editControllerUID =
    SMTG_INLINE_UID (0xBACB8EB9, 0xAFAD4C09, 0x90D5893E, 0xCE6D94AD);

struct AGainAudioProcessorVtbl
{
	Steinberg_Vst_IComponentVtbl component;
	Steinberg_Vst_IConnectionPointVtbl connectionPoint;
	Steinberg_Vst_IAudioProcessorVtbl audioProcessor;
	Steinberg_Vst_IProcessContextRequirementsVtbl processContextRequirements;
};

typedef struct
{
	const struct Steinberg_Vst_IComponentVtbl* componentVtbl;
	const struct Steinberg_Vst_IConnectionPointVtbl* connectionPointVtbl;
	const struct Steinberg_Vst_IAudioProcessorVtbl* audioProcessorVtbl;
	const struct Steinberg_Vst_IProcessContextRequirementsVtbl* processContextRequirementsVtbl;
	Steinberg_int32 refCount;
	struct Steinberg_Vst_IConnectionPoint* connectionPoint;
	float fGain;
} AGainAudioProcessor;

struct AGainEditControllerVtbl
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
	Steinberg_Vst_ParamValue gainParam;
} AGainEditController;

struct AGainFactoryVtbl
{
	Steinberg_IPluginFactory2Vtbl pluginFactory;
};

typedef struct
{
	const struct Steinberg_IPluginFactory2Vtbl* pluginFactoryVtbl;
	struct Steinberg_PClassInfo2 classes[2];
	struct Steinberg_PFactoryInfo factoryInfo;
} AGainFactory;

/*-----------------------------------------------------------------------------------------------------------------------------
Audio Processor Methods*/

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRef (void* thisInterface)
{
	AGainAudioProcessor* instance = (AGainAudioProcessor*)thisInterface;
	instance->refCount += 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRef_ConnectionPoint (void* thisInterface)
{
	return AGainProcessor_AddRef ((void*)((int64_t)thisInterface - pointerOffset));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_AddRef_AudioProcessor (void* thisInterface)
{
	return AGainProcessor_AddRef ((void*)((int64_t)thisInterface - (pointerOffset * 2)));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE
AGainProcessor_AddRef_ProcessContextRequirements (void* thisInterface)
{
	return AGainProcessor_AddRef ((void*)((int64_t)thisInterface - (pointerOffset * 3)));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_Release (void* thisInterface)
{
	AGainAudioProcessor* instance = (AGainAudioProcessor*)thisInterface;
	if (instance->refCount == 1)
	{
		free (instance);
		return 0;
	}
	instance->refCount -= 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_Release_ConnectionPoint (void* thisInterface)
{
	return AGainProcessor_Release ((void*)((int64_t)thisInterface - pointerOffset));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_Release_AudioProcessor (void* thisInterface)
{
	return AGainProcessor_Release ((void*)((int64_t)thisInterface - (pointerOffset * 2)));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE
AGainProcessor_Release_ProcessContextRequirements (void* thisInterface)
{
	return AGainProcessor_Release ((void*)((int64_t)thisInterface - (pointerOffset * 3)));
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterface (void* thisInterface,
                                                                        const Steinberg_TUID iid,
                                                                        void** obj)
{
	AGainAudioProcessor* instance = (AGainAudioProcessor*)thisInterface;
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
		*obj = (void*)((int64_t)instance + pointerOffset);
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IAudioProcessor_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + (pointerOffset * 2));
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IProcessContextRequirements_iid, iid))
	{
		AGainProcessor_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + (pointerOffset * 3));
		return Steinberg_kResultTrue;
	}
	*obj = NULL;
	return Steinberg_kResultFalse;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterface_ConnectionPoint (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainProcessor_QueryInterface ((void*)((int64_t)thisInterface - pointerOffset), iid,
	                                      obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterface_AudioProcessor (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainProcessor_QueryInterface ((void*)((int64_t)thisInterface - (pointerOffset * 2)),
	                                      iid, obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_QueryInterface_ProcessContextRequirements (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainProcessor_QueryInterface ((void*)((int64_t)thisInterface - (pointerOffset * 3)),
	                                      iid, obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Initialize (void* thisInterface, struct Steinberg_FUnknown* context)
{
	return Steinberg_kResultOk;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_Terminate (void* thisInterface)
{
	return Steinberg_kResultOk;
};

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Connect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	AGainAudioProcessor* instance = (AGainAudioProcessor*)((int64_t)thisInterface - pointerOffset);
	instance->connectionPoint = other;
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Disconnect (void* thisInterface, struct Steinberg_Vst_IConnectionPoint* other)
{
	AGainAudioProcessor* instance = (AGainAudioProcessor*)((int64_t)thisInterface - pointerOffset);
	instance->connectionPoint = NULL;
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Notify (void* thisInterface, struct Steinberg_Vst_IMessage* message)
{
	return Steinberg_kResultOk;
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
	return Steinberg_kResultOk;
};

Steinberg_int32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetBusCount (void* thisInterface,
                                                                   Steinberg_Vst_MediaType type,
                                                                   Steinberg_Vst_BusDirection dir)
{
	if (type == Steinberg_Vst_MediaTypes_kAudio)
	{
		return 1;
	}
	return 0;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_GetBusInfo (
    void* thisInterface, Steinberg_Vst_MediaType type, Steinberg_Vst_BusDirection dir,
    Steinberg_int32 index, struct Steinberg_Vst_BusInfo* bus)
{
	if (type == Steinberg_Vst_MediaTypes_kEvent)
	{
		return Steinberg_kResultFalse;
	}
	static const Steinberg_char16 name_string[] = {'b', 'u', 's'};
	memcpy (bus->name, name_string, sizeof (name_string));
	bus->channelCount = 2;
	bus->flags = Steinberg_Vst_BusInfo_BusFlags_kDefaultActive;
	bus->direction = dir;
	bus->mediaType = type;
	bus->busType = Steinberg_Vst_BusTypes_kMain;
	return Steinberg_kResultTrue;
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
	if (type == Steinberg_Vst_MediaTypes_kEvent)
	{
		return Steinberg_kResultFalse;
	}
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetActive (void* thisInterface,
                                                                   Steinberg_TBool state)
{
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetState (void* thisInterface,
                                                                  struct Steinberg_IBStream* state)
{
	if (state == NULL)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainAudioProcessor* instance = (AGainAudioProcessor*)thisInterface;
	return state->lpVtbl->read (state, &instance->fGain, sizeof (instance->fGain), NULL);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_GetState (void* thisInterface,
                                                                  struct Steinberg_IBStream* state)
{
	if (state == NULL)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainAudioProcessor* instance = (AGainAudioProcessor*)thisInterface;
	return state->lpVtbl->write (state, &instance->fGain, sizeof (instance->fGain), NULL);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetBusArrangements (
    void* thisInterface, Steinberg_Vst_SpeakerArrangement* inputs, Steinberg_int32 numIns,
    Steinberg_Vst_SpeakerArrangement* outputs, Steinberg_int32 numOuts)
{
	if (numIns != numOuts || numIns != 1)
	{
		return Steinberg_kResultFalse;
	}
	if (inputs[0] != outputs[0] || inputs[0] != Steinberg_Vst_SpeakerArr_kStereo)
	{
		return Steinberg_kResultFalse;
	}
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_GetBusArrangement (void* thisInterface, Steinberg_Vst_BusDirection dir,
                                  Steinberg_int32 index, Steinberg_Vst_SpeakerArrangement* arr)
{
	if (index != 0)
	{
		return Steinberg_kInvalidArgument;
	}
	*arr = Steinberg_Vst_SpeakerArr_kStereo;
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_CanProcessSampleSize (void* thisInterface, Steinberg_int32 symbolicSampleSize)
{
	return symbolicSampleSize == Steinberg_Vst_SymbolicSampleSizes_kSample32 ?
	           Steinberg_kResultTrue :
	           Steinberg_kResultFalse;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetLatencySamples (void* thisInterface)
{
	return 0;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_SetupProcessing (void* thisInterface, struct Steinberg_Vst_ProcessSetup* setup)
{
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainProcessor_SetProcessing (void* thisInterface,
                                                                       Steinberg_TBool state)
{
	return Steinberg_kResultTrue;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainProcessor_Process (void* thisInterface, struct Steinberg_Vst_ProcessData* data)
{
	AGainAudioProcessor* instance =
	    (AGainAudioProcessor*)((int64_t)thisInterface - (pointerOffset * 2));
	Steinberg_Vst_IParameterChanges* paramChanges = data->inputParameterChanges;
	if (paramChanges)
	{
		Steinberg_int32 numParamsChanged = paramChanges->lpVtbl->getParameterCount (paramChanges);

		for (Steinberg_int32 i = 0; i < numParamsChanged; i++)
		{
			Steinberg_Vst_IParamValueQueue* paramQueue =
			    paramChanges->lpVtbl->getParameterData (paramChanges, i);
			if (paramQueue)
			{
				Steinberg_Vst_ParamValue value;
				Steinberg_int32 sampleOffset;
				Steinberg_int32 numPoints = paramQueue->lpVtbl->getPointCount (paramQueue);
				if (numPoints > 0 &&
				    paramQueue->lpVtbl->getPoint (paramQueue, numPoints - 1, &sampleOffset,
				                                  &value) == Steinberg_kResultTrue)
				{

					instance->fGain = (float)value;
				}
			}
		}
	}
	if (!data || data->numSamples == 0 || data->inputs == 0 || data->outputs == 0)
	{
		return Steinberg_kResultTrue;
	}
	float fGain2 = 2.f * instance->fGain;
	for (int channel_index = 0; channel_index < data->inputs[0].numChannels; channel_index++)
	{
		for (int sample_index = 0; sample_index < data->numSamples; sample_index++)
		{
			float sampleInput =
			    data->inputs[0]
			        .Steinberg_Vst_AudioBusBuffers_channelBuffers32[channel_index][sample_index];
			data->outputs[0]
			    .Steinberg_Vst_AudioBusBuffers_channelBuffers32[channel_index][sample_index] =
			    sampleInput * fGain2;
		}
	}

	return Steinberg_kResultTrue;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainProcessor_GetTailSamples (void* thisInterface)
{
	return 0;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE
AGainProcessor_getProcessContextRequirements (void* thisInterface)
{
	return 0;
}

/*-----------------------------------------------------------------------------------------------------------------------------
Edit Controller methods*/

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_AddRef (void* thisInterface)
{
	AGainEditController* instance = (AGainEditController*)thisInterface;
	instance->refCount += 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_AddRef_ConnectionPoint (void* thisInterface)
{
	return AGainController_AddRef ((void*)((int64_t)thisInterface - pointerOffset));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_AddRef_EditController2 (void* thisInterface)
{
	return AGainController_AddRef ((void*)((int64_t)thisInterface - (pointerOffset * 2)));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainController_Release (void* thisInterface)
{
	AGainEditController* instance = (AGainEditController*)thisInterface;
	if (instance->refCount == 1)
	{
		free (instance);
		return 0;
	}
	instance->refCount -= 1;
	return instance->refCount;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE
AGainController_Release_ConnectionPoint (void* thisInterface)
{
	return AGainController_Release ((void*)((int64_t)thisInterface - pointerOffset));
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE
AGainController_Release_EditController2 (void* thisInterface)
{
	return AGainController_Release ((void*)((int64_t)thisInterface - (pointerOffset * 2)));
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_QueryInterface (void* thisInterface,
                                                                         const Steinberg_TUID iid,
                                                                         void** obj)
{
	AGainEditController* instance = (AGainEditController*)thisInterface;
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
		*obj = (void*)((int64_t)instance + pointerOffset);
		return Steinberg_kResultTrue;
	}
	if (compare_iid (Steinberg_Vst_IEditController2_iid, iid))
	{
		AGainController_AddRef (thisInterface);
		*obj = (void*)((int64_t)instance + (pointerOffset * 2));
		return Steinberg_kResultTrue;
	}
	*obj = NULL;
	return Steinberg_kNoInterface;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_QueryInterface_ConnectionPoint (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainController_QueryInterface ((void*)((int64_t)thisInterface - pointerOffset), iid,
	                                       obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_QueryInterface_EditController2 (
    void* thisInterface, const Steinberg_TUID iid, void** obj)
{
	return AGainController_QueryInterface ((void*)((int64_t)thisInterface - (pointerOffset * 2)),
	                                       iid, obj);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainController_Initialize (void* thisInterface, struct Steinberg_FUnknown* context)
{
	return Steinberg_kResultTrue;
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
	if (state == NULL)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainEditController* instance = (AGainEditController*)thisInterface;
	return state->lpVtbl->read (state, &instance->gainParam, sizeof (instance->gainParam), NULL);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetState (void* thisInterface,
                                                                   struct Steinberg_IBStream* state)
{
	if (state == NULL)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainEditController* instance = (AGainEditController*)thisInterface;
	return state->lpVtbl->write (state, &instance->gainParam, sizeof (instance->gainParam), NULL);
}

Steinberg_int32 SMTG_STDMETHODCALLTYPE AGainController_GetParameterCount (void* thisInterface)
{
	return 1;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParameterInfo (
    void* thisInterface, Steinberg_int32 paramIndex, struct Steinberg_Vst_ParameterInfo* info)
{
	info->defaultNormalizedValue = 0;
	info->id = 55;
	info->stepCount = 0;
	info->flags = Steinberg_Vst_ParameterInfo_ParameterFlags_kCanAutomate;
	info->defaultNormalizedValue = 0.5f;
	info->unitId = Steinberg_Vst_kRootUnitId;
	static const Steinberg_char16 title_string[] = {'G', 'a', 'i', 'n'};
	memcpy (info->title, title_string, sizeof (title_string));
	static const Steinberg_char16 units_string[] = {'d', 'B'};
	memcpy (info->units, units_string, sizeof (units_string));

	return Steinberg_kResultTrue;
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE AGainController_NormalizedParamToPlain (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue valueNormalized)
{
	return 6.02061f + 20 * log10f ((float)valueNormalized);
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE AGainController_PlainParamToNormalized (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue plainValue)
{
	return expf (logf (10.f) * ((float)plainValue - 6.02061f) / 20.f);
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParamStringByValue (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue valueNormalized,
    Steinberg_Vst_String128 string)
{
	Steinberg_Vst_ParamValue plainValue =
	    AGainController_NormalizedParamToPlain (thisInterface, id, valueNormalized);

	char buffer[32];
	snprintf (buffer, 31, "%f", plainValue);
	buffer[31] = 0;

	char* bufptr = buffer;
	while (*bufptr != '\0')
	{
		*string = *bufptr;
		++string;
		++bufptr;
	}
	return Steinberg_kResultOk;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_GetParamValueByString (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_TChar* string,
    Steinberg_Vst_ParamValue* valueNormalized)
{
	return Steinberg_kNotImplemented;
}

Steinberg_Vst_ParamValue SMTG_STDMETHODCALLTYPE
AGainController_GetParamNormalized (void* thisInterface, Steinberg_Vst_ParamID id)
{
	AGainEditController* instance = (AGainEditController*)thisInterface;
	return instance->gainParam;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_SetParamNormalized (
    void* thisInterface, Steinberg_Vst_ParamID id, Steinberg_Vst_ParamValue value)
{
	AGainEditController* instance = (AGainEditController*)thisInterface;
	instance->gainParam = value;
	return Steinberg_kResultTrue;
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

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainController_OpenAboutBox (void* thisInterface,
                                                                       Steinberg_TBool onlyCheck)
{
	return Steinberg_kNotImplemented;
}

static const struct AGainAudioProcessorVtbl kAGainAudioProcessorVtbl = {
    {AGainProcessor_QueryInterface, AGainProcessor_AddRef, AGainProcessor_Release,
     AGainProcessor_Initialize, AGainProcessor_Terminate, AGainProcessor_GetControllerClassId,
     AGainProcessor_SetIoMode, AGainProcessor_GetBusCount, AGainProcessor_GetBusInfo,
     AGainProcessor_GetRoutingInfo, AGainProcessor_ActivateBus, AGainProcessor_SetActive,
     AGainProcessor_SetState, AGainProcessor_GetState},
    {AGainProcessor_QueryInterface_ConnectionPoint, AGainProcessor_AddRef_ConnectionPoint,
     AGainProcessor_Release_ConnectionPoint, AGainProcessor_Connect, AGainProcessor_Disconnect,
     AGainProcessor_Notify},
    {AGainProcessor_QueryInterface_AudioProcessor, AGainProcessor_AddRef_AudioProcessor,
     AGainProcessor_Release_AudioProcessor, AGainProcessor_SetBusArrangements,
     AGainProcessor_GetBusArrangement, AGainProcessor_CanProcessSampleSize,
     AGainProcessor_GetLatencySamples, AGainProcessor_SetupProcessing, AGainProcessor_SetProcessing,
     AGainProcessor_Process, AGainProcessor_GetTailSamples},
    {AGainProcessor_QueryInterface_ProcessContextRequirements,
     AGainProcessor_AddRef_ProcessContextRequirements,
     AGainProcessor_Release_ProcessContextRequirements,
     AGainProcessor_getProcessContextRequirements},
};

static const struct AGainEditControllerVtbl kAGainEditControllerVtbl = {
    {AGainController_QueryInterface, AGainController_AddRef, AGainController_Release,
     AGainController_Initialize, AGainController_Terminate, AGainController_SetComponentState,
     AGainController_SetState, AGainController_GetState, AGainController_GetParameterCount,
     AGainController_GetParameterInfo, AGainController_GetParamStringByValue,
     AGainController_GetParamValueByString, AGainController_NormalizedParamToPlain,
     AGainController_PlainParamToNormalized, AGainController_GetParamNormalized,
     AGainController_SetParamNormalized, AGainController_SetComponentHandler,
     AGainController_CreateView},
    {AGainController_QueryInterface_ConnectionPoint, AGainController_AddRef_ConnectionPoint,
     AGainController_Release_ConnectionPoint, AGainController_Connect, AGainController_Disconnect,
     AGainController_Notify},
    {AGainController_QueryInterface_EditController2, AGainController_AddRef_EditController2,
     AGainController_Release_EditController2, AGainController_SetKnobMode, AGainController_OpenHelp,
     AGainController_OpenAboutBox}};

/* methods derived from "Steinberg_FUnknown": */
Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainFactory_AddRef (void* thisInterface)
{
	return 100;
}

Steinberg_uint32 SMTG_STDMETHODCALLTYPE AGainFactory_Release (void* thisInterface)
{
	return 100;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainFactory_QueryInterface (void* thisInterface,
                                                                      const Steinberg_TUID iid,
                                                                      void** obj)
{
	if (compare_iid (iid, Steinberg_FUnknown_iid))
	{
		AGainFactory_AddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (iid, Steinberg_IPluginFactory_iid))
	{
		AGainFactory_AddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid (iid, Steinberg_IPluginFactory2_iid))
	{
		AGainFactory_AddRef (thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	*obj = NULL;
	return Steinberg_kNoInterface;
}

/* methods derived from "Steinberg_IPluginFactory": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE
AGainFactory_GetFactoryInfo (void* thisInterface, struct Steinberg_PFactoryInfo* info)
{
	if (info == 0)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainFactory* factory = (AGainFactory*)thisInterface;
	memcpy (info, &factory->factoryInfo, sizeof (struct Steinberg_PFactoryInfo));
	return Steinberg_kResultTrue;
}

Steinberg_int32 SMTG_STDMETHODCALLTYPE AGainFactory_CountClasses (void* thisInterface)
{
	return 2;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainFactory_GetClassInfo (
    void* thisInterface, Steinberg_int32 index, struct Steinberg_PClassInfo* info)
{
	return Steinberg_kNotImplemented;
}

Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainFactory_CreateInstance (void* thisInterface,
                                                                      Steinberg_FIDString cid,
                                                                      Steinberg_FIDString iid,
                                                                      void** obj)
{
	AGainFactory* factory = (AGainFactory*)thisInterface;
	if (compare_iid (cid, factory->classes[0].cid))
	{
		AGainAudioProcessor* instance = (AGainAudioProcessor*)malloc (sizeof (AGainAudioProcessor));
		instance->componentVtbl = &kAGainAudioProcessorVtbl.component;
		instance->connectionPointVtbl = &kAGainAudioProcessorVtbl.connectionPoint;
		instance->audioProcessorVtbl = &kAGainAudioProcessorVtbl.audioProcessor;
		instance->processContextRequirementsVtbl =
		    &kAGainAudioProcessorVtbl.processContextRequirements;
		instance->refCount = 0;
		instance->connectionPoint = NULL;
		instance->fGain = 0.5f;
		return instance->componentVtbl->queryInterface (instance, iid, obj);
	}
	if (compare_iid (cid, factory->classes[1].cid))
	{
		AGainEditController* instance = (AGainEditController*)malloc (sizeof (AGainEditController));
		instance->editControllerVtbl = &kAGainEditControllerVtbl.editController;
		instance->connectionPointVtbl = &kAGainEditControllerVtbl.connectionPoint;
		instance->editController2Vtbl = &kAGainEditControllerVtbl.editController2;
		instance->refCount = 0;
		instance->gainParam = 0.5f;
		*obj = instance;
		return instance->editControllerVtbl->queryInterface (instance, iid, obj);
	}
	return Steinberg_kResultFalse;
}

/* methods defined in "Steinberg_IPluginFactory2": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE AGainFactory_GetClassInfo2 (
    void* thisInterface, Steinberg_int32 index, struct Steinberg_PClassInfo2* info)
{
	if (index > 1 || info == 0)
	{
		return Steinberg_kInvalidArgument;
	}
	AGainFactory* factory = (AGainFactory*)thisInterface;
	memcpy (info, &factory->classes[index], sizeof (struct Steinberg_PClassInfo2));
	return Steinberg_kResultTrue;
}

static const struct AGainFactoryVtbl kAGainPluginFactoryVtbl = {
    {AGainFactory_QueryInterface, AGainFactory_AddRef, AGainFactory_Release,
     AGainFactory_GetFactoryInfo, AGainFactory_CountClasses, AGainFactory_GetClassInfo,
     AGainFactory_CreateInstance, AGainFactory_GetClassInfo2}};

#ifndef SMTG_EXPORT_SYMBOL
#if __APPLE__
#define SMTG_EXPORT_SYMBOL __attribute__ ((visibility ("default")))
#else
#define SMTG_EXPORT_SYMBOL __declspec (dllexport)
#endif
#endif // SMTG_EXPORT_SYMBOL

SMTG_EXPORT_SYMBOL Steinberg_IPluginFactory* SMTG_STDMETHODCALLTYPE GetPluginFactory ()
{
	static AGainFactory againFactory;
	static int32_t once = 1;
	if (once)
	{
		once = 0;

		againFactory.pluginFactoryVtbl = &kAGainPluginFactoryVtbl.pluginFactory;

		strcpy (againFactory.factoryInfo.vendor, "Steinberg");
		strcpy (againFactory.factoryInfo.email, "info@steinberg.net");
		strcpy (againFactory.factoryInfo.url, "steinberg.net");
		againFactory.factoryInfo.flags = 16;

		memcpy (againFactory.classes[0].cid, audioProcessorUID, sizeof (Steinberg_TUID));
		againFactory.classes[0].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
		strcpy (againFactory.classes[0].category, "Audio Module Class");
		strcpy (againFactory.classes[0].name, "C-AGain");
		againFactory.classes[0].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
		strcpy (againFactory.classes[0].subCategories, "Fx");
		strcpy (againFactory.classes[0].vendor, "Steinberg");
		strcpy (againFactory.classes[0].version, "1.0.0");
		strcpy (againFactory.classes[0].sdkVersion, "3.7.6");

		memcpy (againFactory.classes[1].cid, editControllerUID, sizeof (Steinberg_TUID));
		againFactory.classes[1].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
		strcpy (againFactory.classes[1].category, "Component Controller Class");
		strcpy (againFactory.classes[1].name, "C-AGain");
		againFactory.classes[1].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
		strcpy (againFactory.classes[1].subCategories, "Fx");
		strcpy (againFactory.classes[1].vendor, "Steinberg");
		strcpy (againFactory.classes[1].version, "1.0.0");
		strcpy (againFactory.classes[1].sdkVersion, "3.7.6");
	}

	return (Steinberg_IPluginFactory*)&againFactory;
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

#else

SMTG_EXPORT_SYMBOL Steinberg_TBool InitDll ()
{
	return 1;
}

SMTG_EXPORT_SYMBOL Steinberg_TBool ExitDll ()
{
	return 1;
}

#endif // __APPLE__
