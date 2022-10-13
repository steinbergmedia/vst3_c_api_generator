#include <assert.h>

#include "vst3_c_api.h"


int main ()
{
	/*ipluginbase.h*/
	assert (sizeof(struct Steinberg_PFactoryInfo) == 452);
	assert (sizeof(struct Steinberg_PClassInfo) == 116);
	assert (sizeof(struct Steinberg_PClassInfo2) == 440);
	assert (sizeof(struct Steinberg_PClassInfoW) == 696);

	/*ivstaudioprocessor.h*/
	assert (sizeof(struct Steinberg_Vst_ProcessSetup) == 24);
	assert (sizeof(struct Steinberg_Vst_AudioBusBuffers) == 24);
	assert (sizeof(struct Steinberg_Vst_ProcessData) == 80);

	/*ivstcomponent.h*/
	assert (sizeof(struct Steinberg_Vst_BusInfo) == 276);
	assert (sizeof(struct Steinberg_Vst_RoutingInfo) == 12);

	/*ivstcontextmenu.h*/
	assert (sizeof(struct Steinberg_Vst_IContextMenuItem) == 264);

	/*ivsteditcontroller.h*/
	assert (sizeof(struct Steinberg_Vst_ParameterInfo) == 792);

	/*ivstevents.h*/
	assert (sizeof(struct Steinberg_Vst_NoteOnEvent) == 20);
	assert (sizeof(struct Steinberg_Vst_NoteOffEvent) == 16);
	assert (sizeof(struct Steinberg_Vst_DataEvent) == 16);
	assert (sizeof(struct Steinberg_Vst_PolyPressureEvent) == 12);
	assert (sizeof(struct Steinberg_Vst_ChordEvent) == 16);
	assert (sizeof(struct Steinberg_Vst_ScaleEvent) == 16);
	assert (sizeof(struct Steinberg_Vst_LegacyMIDICCOutEvent) == 4);
	assert (sizeof(struct Steinberg_Vst_Event) == 48);

	/*ivstnoteexpression.h*/
	assert (sizeof(struct Steinberg_Vst_NoteExpressionValueDescription) == 32);
	assert (sizeof(struct Steinberg_Vst_NoteExpressionValueEvent) == 16);
	assert (sizeof(struct Steinberg_Vst_NoteExpressionTextEvent) == 24);
	assert (sizeof(struct Steinberg_Vst_NoteExpressionTypeInfo) == 816);
	assert (sizeof(struct Steinberg_Vst_KeyswitchInfo) == 536);

	/*ivstprocesscontext.h*/
	assert (sizeof(struct Steinberg_Vst_FrameRate) == 8);
	assert (sizeof(struct Steinberg_Vst_Chord) == 4);
	assert (sizeof(struct Steinberg_Vst_ProcessContext) == 112);

	/*ivstrepresentation.h*/
	assert (sizeof(struct Steinberg_Vst_RepresentationInfo) == 256);

	/*ivstunits.h*/
	assert (sizeof(struct Steinberg_Vst_UnitInfo) == 268);
	assert (sizeof(struct Steinberg_Vst_ProgramListInfo) == 264);

	return 0;
}
