#include "test_header.h"
#include "memory.h"
#include "string.h"


int compare_iid(const Steinberg_TUID id1, const Steinberg_TUID id2) {
	return memcmp(id1, id2, sizeof(Steinberg_TUID)) == 0;
}

/* methods derived from "Steinberg_FUnknown": */
Steinberg_uint32 SMTG_STDMETHODCALLTYPE myAddRef(void* thisInterface) {
	return 100;
}
Steinberg_uint32 SMTG_STDMETHODCALLTYPE myRelease(void* thisInterface) {
	return 100;
}
Steinberg_tresult SMTG_STDMETHODCALLTYPE myQueryInterface (void* thisInterface, const Steinberg_TUID iid, void** obj){
	if (compare_iid(iid, Steinberg_FUnknown_iid)) {
		myAddRef(thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid(iid, Steinberg_IPluginFactory_iid)) {
		myAddRef(thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	if (compare_iid(iid, Steinberg_IPluginFactory2_iid)) {
		myAddRef(thisInterface);
		*obj = thisInterface;
		return Steinberg_kResultTrue;
	}
	return Steinberg_kNoInterface;
}

/* methods derived from "Steinberg_IPluginFactory": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetFactoryInfo (void* thisInterface, struct Steinberg_PFactoryInfo* info){
	if (info == 0) {
		return Steinberg_kInvalidArgument;
	}
	strcpy(info->vendor, "test_vendor");
	strcpy(info->email, "test_email");
	strcpy(info->url, "test_url");
	info->flags = 16;
	return Steinberg_kResultTrue;
}
Steinberg_int32 SMTG_STDMETHODCALLTYPE myCountClasses (void* thisInterface){
	return 2;
}
static struct Steinberg_PClassInfo2 classes[2];

Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetClassInfo (void* thisInterface, Steinberg_int32 index, struct Steinberg_PClassInfo* info){}
Steinberg_tresult SMTG_STDMETHODCALLTYPE myCreateInstance (void* thisInterface, Steinberg_FIDString cid, Steinberg_FIDString iid, void** obj){}

/* methods defined in "Steinberg_IPluginFactory2": */
Steinberg_tresult SMTG_STDMETHODCALLTYPE myGetClassInfo2 (void* thisInterface, Steinberg_int32 index, struct Steinberg_PClassInfo2* info){
	if (index > 1 || info == 0) {
		return Steinberg_kInvalidArgument;
	}
	memcpy(info, &classes[index], sizeof(struct Steinberg_PClassInfo2));
	return Steinberg_kResultTrue;
}

static const Steinberg_IPluginFactory2Vtbl myPluginFactoryVtbl = {
	myQueryInterface,
	myAddRef,
	myRelease,
	myGetFactoryInfo,
	myCountClasses,
	myGetClassInfo,
	myCreateInstance,
	myGetClassInfo2
};

static  Steinberg_IPluginFactory2 myPluginFactory = {&myPluginFactoryVtbl };

__declspec (dllexport) Steinberg_IPluginFactory* SMTG_STDMETHODCALLTYPE GetPluginFactory(){
	static const Steinberg_TUID audioProcessorUID = SMTG_INLINE_UID(0x84E8DE5F, 0x92554F53, 0x96FAE413, 0x3C935A18);
	memcpy(classes[0].cid, audioProcessorUID, sizeof(Steinberg_TUID));
	classes[0].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
	strcpy(classes[0].category, "Audio Module Class");
	static const Steinberg_char16 name[] = {'A', 'G', 'A', 'I', 'N'};
	memcpy(classes[0].name, name, sizeof(name));
	classes[0].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
	strcpy(classes[0].subCategories, "Fx");
	classes[0].vendor[0] = 0;
	classes[0].version[0] = 0;
	classes[0].sdkVersion[0] = 0;

	static const Steinberg_TUID editControllerUID = SMTG_INLINE_UID(0xD39D5B65, 0xD7AF42FA, 0x843F4AC8, 0x41EB04F0);
	memcpy(classes[1].cid, editControllerUID, sizeof(Steinberg_TUID));
	classes[1].cardinality = Steinberg_PClassInfo_ClassCardinality_kManyInstances;
	strcpy(classes[1].category, "Component Controller Class");
	static const Steinberg_char16 name2[] = { 'A', 'G', 'A', 'I', 'N' };
	memcpy(classes[1].name, name2, sizeof(name2));
	classes[1].classFlags = Steinberg_Vst_ComponentFlags_kDistributable;
	strcpy(classes[1].subCategories, "Fx");
	classes[1].vendor[0] = 0;
	classes[1].version[0] = 0;
	classes[1].sdkVersion[0] = 0;

	return &myPluginFactory;
}
