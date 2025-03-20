#pragma once

#include "funknown.h"
#include "structs.h"

namespace Steinberg {

class IPluginFactory : public FUnknown
{
	virtual tresult PLUGIN_API getFactoryInfo (PFactoryInfo* info) = 0;
	virtual int32 PLUGIN_API countClasses () = 0;
	virtual tresult PLUGIN_API createInstance (const FIDString& cid, FIDString _iid, void** obj) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IPluginFactory, 0x7A4D811C, 0x52114A1F, 0xAED9D2EE, 0x0B43BF9F)

class IPluginFactory2 : public IPluginFactory
{
	virtual tresult PLUGIN_API getClassInfo2 (const int32* const index, PClassInfo2* info) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IPluginFactory2, 0x0007B650, 0xF24B4C0B, 0xA464EDB9, 0xF00B2ABB)

class IPluginFactory3 : public IPluginFactory2
{
	virtual tresult PLUGIN_API getClassInfoUnicode (int32 index, PClassInfoW*& info) = 0;
	virtual tresult PLUGIN_API setHostContext (FUnknown* context) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IPluginFactory3, 0x4555A2AB, 0xC1234E57, 0x9B122910, 0x36878931)

class IPlugViewContentScaleSupport : public FUnknown
{
	typedef float ScaleFactor;

	virtual tresult PLUGIN_API setContentScaleFactor (ScaleFactor factor /*in*/) = 0;

	static const FUID iid;
};

DECLARE_CLASS_IID (IPlugViewContentScaleSupport, 0x65ED9690, 0x8AC44525, 0x8AADEF7A, 0x72EA703F)

}