//-----------------------------------------------------------------------------
// This file is part of a Steinberg SDK. It is subject to the license terms
// in the LICENSE file found in the top-level directory of this distribution
// and at www.steinberg.net/sdklicenses. 
// No part of the SDK, including this file, may be copied, modified, propagated,
// or distributed except according to the terms contained in the LICENSE file.
//-----------------------------------------------------------------------------

#include "pluginterfaces/vst/vsttypes.h"
#include "pluginterfaces/base/ipluginbase.h"
#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "pluginterfaces/vst/ivstcomponent.h"
#include "pluginterfaces/vst/ivstcontextmenu.h"
#include "pluginterfaces/vst/ivsteditcontroller.h"
#include "pluginterfaces/vst/ivstevents.h"
#include "pluginterfaces/vst/ivstnoteexpression.h"
#include "pluginterfaces/vst/ivstprocesscontext.h"
#include "pluginterfaces/vst/ivstrepresentation.h"
#include "pluginterfaces/vst/ivstunits.h"

extern "C" {
#include "vst3_c_api.h"
}

namespace Steinberg {

/*ipluginbase.h*/
static_assert (sizeof (struct Steinberg_PFactoryInfo) == sizeof (PFactoryInfo));
static_assert (sizeof (struct Steinberg_PClassInfo) == sizeof (PClassInfo));
static_assert (sizeof (struct Steinberg_PClassInfo2) == sizeof (PClassInfo2));
static_assert (sizeof (struct Steinberg_PClassInfoW) == sizeof (PClassInfoW));

/*ivstaudioprocessor.h*/
static_assert (sizeof (struct Steinberg_Vst_ProcessSetup) == sizeof (Vst::ProcessSetup));
static_assert (sizeof (struct Steinberg_Vst_AudioBusBuffers) == sizeof (Vst::AudioBusBuffers));
static_assert (sizeof (struct Steinberg_Vst_ProcessData) == sizeof (Vst::ProcessData));

/*ivstcomponent.h*/
static_assert (sizeof (struct Steinberg_Vst_BusInfo) == sizeof (Vst::BusInfo));
static_assert (sizeof (struct Steinberg_Vst_RoutingInfo) == sizeof (Vst::RoutingInfo));

/*ivstcontextmenu.h*/
static_assert (sizeof (struct Steinberg_Vst_IContextMenuItem) == sizeof (Vst::IContextMenuItem));

/*ivsteditcontroller.h*/
static_assert (sizeof (struct Steinberg_Vst_ParameterInfo) == sizeof (Vst::ParameterInfo));

/*ivstevents.h*/
static_assert (sizeof (struct Steinberg_Vst_NoteOnEvent) == sizeof (Vst::NoteOnEvent));
static_assert (sizeof (struct Steinberg_Vst_NoteOffEvent) == sizeof (Vst::NoteOffEvent));
static_assert (sizeof (struct Steinberg_Vst_DataEvent) == sizeof (Vst::DataEvent));
static_assert (sizeof (struct Steinberg_Vst_PolyPressureEvent) == sizeof (Vst::PolyPressureEvent));
static_assert (sizeof (struct Steinberg_Vst_ChordEvent) == sizeof (Vst::ChordEvent));
static_assert (sizeof (struct Steinberg_Vst_ScaleEvent) == sizeof (Vst::ScaleEvent));
static_assert (sizeof (struct Steinberg_Vst_LegacyMIDICCOutEvent) == sizeof (Vst::LegacyMIDICCOutEvent));
static_assert (sizeof (struct Steinberg_Vst_Event) == sizeof (Vst::Event));

/*ivstnoteexpression.h*/
static_assert (sizeof (struct Steinberg_Vst_NoteExpressionValueDescription) == sizeof (Vst::NoteExpressionValueDescription));
static_assert (sizeof (struct Steinberg_Vst_NoteExpressionValueEvent) == sizeof (Vst::NoteExpressionValueEvent));
static_assert (sizeof (struct Steinberg_Vst_NoteExpressionTextEvent) == sizeof (Vst::NoteExpressionTextEvent));
static_assert (sizeof (struct Steinberg_Vst_NoteExpressionTypeInfo) == sizeof (Vst::NoteExpressionTypeInfo));
static_assert (sizeof (struct Steinberg_Vst_KeyswitchInfo) == sizeof (Vst::KeyswitchInfo));

/*ivstprocesscontext.h*/
static_assert (sizeof (struct Steinberg_Vst_FrameRate) == sizeof (Vst::FrameRate));
static_assert (sizeof (struct Steinberg_Vst_Chord) == sizeof (Vst::Chord));
static_assert (sizeof (struct Steinberg_Vst_ProcessContext) == sizeof (Vst::ProcessContext));

/*ivstrepresentation.h*/
static_assert (sizeof (struct Steinberg_Vst_RepresentationInfo) == sizeof (Vst::RepresentationInfo));

/*ivstunits.h*/
static_assert (sizeof (struct Steinberg_Vst_UnitInfo) == sizeof (Vst::UnitInfo));
static_assert (sizeof (struct Steinberg_Vst_ProgramListInfo) == sizeof (Vst::ProgramListInfo));

} // namespace

