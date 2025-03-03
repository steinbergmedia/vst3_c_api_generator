typedef struct Steinberg_FUnknownVtbl
{
    /* methods defined in "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

} Steinberg_FUnknownVtbl;

typedef struct Steinberg_FUnknown
{
    struct Steinberg_FUnknownVtbl* lpVtbl;
} Steinberg_FUnknown;

static const Steinberg_TUID Steinberg_FUnknown_iid = SMTG_INLINE_UID (0x00000000, 0x00000000, 0xC0000000, 0x00000046);

typedef struct Steinberg_IPluginFactoryVtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods defined in "Steinberg_IPluginFactory": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getFactoryInfo) (void* thisInterface, struct Steinberg_PFactoryInfo* info);
    Steinberg_int32 (SMTG_STDMETHODCALLTYPE* countClasses) (void* thisInterface);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* createInstance) (void* thisInterface, const Steinberg_FIDString* cid, Steinberg_FIDString iid, void** obj);

} Steinberg_IPluginFactoryVtbl;

typedef struct Steinberg_IPluginFactory
{
    struct Steinberg_IPluginFactoryVtbl* lpVtbl;
} Steinberg_IPluginFactory;

static const Steinberg_TUID Steinberg_IPluginFactory_iid = SMTG_INLINE_UID (0x7A4D811C, 0x52114A1F, 0xAED9D2EE, 0x0B43BF9F);

typedef struct Steinberg_IPluginFactory2Vtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods derived from "Steinberg_IPluginFactory": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getFactoryInfo) (void* thisInterface, struct Steinberg_PFactoryInfo* info);
    Steinberg_int32 (SMTG_STDMETHODCALLTYPE* countClasses) (void* thisInterface);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* createInstance) (void* thisInterface, const Steinberg_FIDString* cid, Steinberg_FIDString iid, void** obj);

    /* methods defined in "Steinberg_IPluginFactory2": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getClassInfo2) (void* thisInterface, const Steinberg_int32* const index, struct Steinberg_PClassInfo2* info);

} Steinberg_IPluginFactory2Vtbl;

typedef struct Steinberg_IPluginFactory2
{
    struct Steinberg_IPluginFactory2Vtbl* lpVtbl;
} Steinberg_IPluginFactory2;

static const Steinberg_TUID Steinberg_IPluginFactory2_iid = SMTG_INLINE_UID (0x0007B650, 0xF24B4C0B, 0xA464EDB9, 0xF00B2ABB);

typedef struct Steinberg_IPluginFactory3Vtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods derived from "Steinberg_IPluginFactory": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getFactoryInfo) (void* thisInterface, struct Steinberg_PFactoryInfo* info);
    Steinberg_int32 (SMTG_STDMETHODCALLTYPE* countClasses) (void* thisInterface);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* createInstance) (void* thisInterface, const Steinberg_FIDString* cid, Steinberg_FIDString iid, void** obj);

    /* methods derived from "Steinberg_IPluginFactory2": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getClassInfo2) (void* thisInterface, const Steinberg_int32* const index, struct Steinberg_PClassInfo2* info);

    /* methods defined in "Steinberg_IPluginFactory3": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getClassInfoUnicode) (void* thisInterface, Steinberg_int32 index, struct Steinberg_PClassInfoW** info);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* setHostContext) (void* thisInterface, struct Steinberg_FUnknown* context);

} Steinberg_IPluginFactory3Vtbl;

typedef struct Steinberg_IPluginFactory3
{
    struct Steinberg_IPluginFactory3Vtbl* lpVtbl;
} Steinberg_IPluginFactory3;

static const Steinberg_TUID Steinberg_IPluginFactory3_iid = SMTG_INLINE_UID (0x4555A2AB, 0xC1234E57, 0x9B122910, 0x36878931);