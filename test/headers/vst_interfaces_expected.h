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

static Steinberg_TUID Steinberg_FUnknown_iid = SMTG_INLINE_UID (0x00000000, 0x00000000, 0xC0000000, 0x00000046);

typedef struct Steinberg_Vst_IUnitHandlerVtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods defined in "Steinberg_Vst_IUnitHandler": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyUnitSelection) (void* thisInterface, Steinberg_UnitID unitId);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyProgramListChange) (void* thisInterface, Steinberg_ProgramListID listId, Steinberg_int32 programIndex);

} Steinberg_Vst_IUnitHandlerVtbl;

typedef struct Steinberg_Vst_IUnitHandler
{
    struct Steinberg_Vst_IUnitHandlerVtbl* lpVtbl;
} Steinberg_Vst_IUnitHandler;

static Steinberg_TUID Steinberg_Vst_IUnitHandler_iid = SMTG_INLINE_UID (0x4B5147F8, 0x4654486B, 0x8DAB30BA, 0x163A3C56);

typedef struct Steinberg_Vst_IUnitHandler2Vtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods defined in "Steinberg_Vst_IUnitHandler2": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyUnitByBusChange) (void* thisInterface);

} Steinberg_Vst_IUnitHandler2Vtbl;

typedef struct Steinberg_Vst_IUnitHandler2
{
    struct Steinberg_Vst_IUnitHandler2Vtbl* lpVtbl;
} Steinberg_Vst_IUnitHandler2;

static Steinberg_TUID Steinberg_Vst_IUnitHandler2_iid = SMTG_INLINE_UID (0xF89F8CDF, 0x699E4BA5, 0x96AAC9A4, 0x81452B01);

typedef struct Steinberg_Vst_IUnitInfoVtbl
{
    /* methods derived from "Steinberg_FUnknown": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* queryInterface) (void* thisInterface, const Steinberg_TUID iid, void** obj);
    Steinberg_uint32 (SMTG_STDMETHODCALLTYPE* addRef) (void* thisInterface);

    /* methods derived from "Steinberg_Vst_IUnitHandler2": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyUnitByBusChange) (void* thisInterface);

    /* methods derived from "Steinberg_Vst_IUnitHandler": */
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyUnitSelection) (void* thisInterface, Steinberg_UnitID unitId);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* notifyProgramListChange) (void* thisInterface, Steinberg_ProgramListID listId, Steinberg_int32 programIndex);

    /* methods defined in "Steinberg_Vst_IUnitInfo": */
    Steinberg_int32 (SMTG_STDMETHODCALLTYPE* getUnitCount) (void* thisInterface);
    Steinberg_tresult (SMTG_STDMETHODCALLTYPE* getUnitInfo) (void* thisInterface, Steinberg_int32 unitIndex, struct Steinberg_Vst_UnitInfo* info);

} Steinberg_Vst_IUnitInfoVtbl;

typedef struct Steinberg_Vst_IUnitInfo
{
    struct Steinberg_Vst_IUnitInfoVtbl* lpVtbl;
} Steinberg_Vst_IUnitInfo;

static Steinberg_TUID Steinberg_Vst_IUnitInfo_iid = SMTG_INLINE_UID (0x3D4BD6B5, 0x913A4FD2, 0xA886E768, 0xA5EB92C1);