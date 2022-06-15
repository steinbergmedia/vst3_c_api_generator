//------------------------------------------------------------------------
// Project     : VST SDK
//
// Category    : Interfaces
// Filename    : pluginterfaces/vst/header_compilation.h
// Created by  : Steinberg, 09/2005
// Description : VST Edit Controller Interfaces
//
//-----------------------------------------------------------------------------
// This file is part of a Steinberg SDK. It is subject to the license terms
// in the LICENSE file found in the top-level directory of this distribution
// and at www.steinberg.net/sdklicenses.
// No part of the SDK, including this file, may be copied, modified, propagated,
// or distributed except according to the terms contained in the LICENSE file.
//-----------------------------------------------------------------------------

#pragma once

#include "pluginterfaces-src/base/fplatform.h"
#include "pluginterfaces-src/base/ftypes.h"
#include "pluginterfaces-src/base/smartpointer.h"
#include "pluginterfaces-src/base/funknown.h"
#include "pluginterfaces-src/base/pluginbasefwd.h"
#include "pluginterfaces-src/base/geoconstants.h"
#include "pluginterfaces-src/base/falignpush.h"
#include "pluginterfaces-src/base/falignpop.h"
#include "pluginterfaces-src/base/fstrdefs.h"
#include "pluginterfaces-src/base/ustring.h"
#include "pluginterfaces-src/base/ucolorspec.h"
#include "pluginterfaces-src/base/typesizecheck.h"
#include "pluginterfaces-src/base/keycodes.h"
#include "pluginterfaces-src/base/iupdatehandler.h"
#include "pluginterfaces-src/base/istringresult.h"
#include "pluginterfaces-src/base/ipersistent.h"
#include "pluginterfaces-src/base/ierrorcontext.h"
#include "pluginterfaces-src/base/icloneable.h"
#include "pluginterfaces-src/base/ibstream.h"
#include "pluginterfaces-src/base/futils.h"
#include "pluginterfaces-src/base/conststringtable.h"
#include "pluginterfaces-src/base/ipluginbase.h"
#include "pluginterfaces-src/base/fvariant.h"
#include "pluginterfaces-src/base/funknownimpl.h"


#include "pluginterfaces-src/vst/ivstmidicontrollers.h"
#include "pluginterfaces-src/vst/vstpshpack4.h"
#include "pluginterfaces-src/vst/vsttypes.h"
#include "pluginterfaces-src/vst/ivsteditcontroller.h"
#include "pluginterfaces-src/vst/vstspeaker.h"
#include "pluginterfaces-src/vst/vstpresetkeys.h"
#include "pluginterfaces-src/vst/ivstunits.h"
#include "pluginterfaces-src/vst/ivstrepresentation.h"
#include "pluginterfaces-src/vst/ivstprocesscontext.h"
#include "pluginterfaces-src/vst/ivstplugview.h"
#include "pluginterfaces-src/vst/ivstpluginterfacesupport.h"
#include "pluginterfaces-src/vst/ivstparameterfunctionname.h"
#include "pluginterfaces-src/vst/ivstparameterchanges.h"
#include "pluginterfaces-src/vst/ivstnoteexpression.h"
#include "pluginterfaces-src/vst/ivstmidilearn.h"
#include "pluginterfaces-src/vst/ivstinterappaudio.h"
#include "pluginterfaces-src/vst/ivstcontextmenu.h"
#include "pluginterfaces-src/vst/ivstautomationstate.h"
#include "pluginterfaces-src/vst/ivstattributes.h"
#include "pluginterfaces-src/vst/ivstcomponent.h"
#include "pluginterfaces-src/vst/ivstaudioprocessor.h"
#include "pluginterfaces-src/vst/ivstchannelcontextinfo.h"
#include "pluginterfaces-src/vst/ivstevents.h"
#include "pluginterfaces-src/vst/ivstmessage.h"
#include "pluginterfaces-src/vst/ivsthostapplication.h"
#include "pluginterfaces-src/vst/ivstphysicalui.h"
#include "pluginterfaces-src/vst/ivstprefetchablesupport.h"
#include "pluginterfaces-src/vst/ivsttestplugprovider.h"
