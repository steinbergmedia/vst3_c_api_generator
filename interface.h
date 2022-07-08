class FUnknown
{
public:

	virtual tresult PLUGIN_API queryInterface (const TUID _iid, void** obj) = 0;

	virtual uint32 PLUGIN_API addRef () = 0;

	static const FUID iid;

};


DECLARE_CLASS_IID (FUnknown, 0x00000000, 0x00000000, 0xC0000000, 0x00000046)