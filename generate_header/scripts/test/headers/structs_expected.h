struct Steinberg_PFactoryInfo
{
    Steinberg_char8 vendor[256 << 4 >> 3 | 1];
    Steinberg_char8 url[256];
    Steinberg_char8 email[256 << 4];
    Steinberg_int32 flags;
    Steinberg_TUID cid;
    union
    {
        int Steinberg_PFactoryInfo_noteOn;
        int Steinberg_PFactoryInfo_noteOff;
    };
};