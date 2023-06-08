from typing import NewType, TypedDict


class TMixerParams(TypedDict):
    fake: bool
    commit: bool


Int8 = NewType("Int8", int)
Int16 = NewType("Int16", int)
Int32 = NewType("Int32", int)
Int64 = NewType("Int64", int)
UInt8 = NewType("UInt8", int)
UInt16 = NewType("UInt16", int)
UInt32 = NewType("UInt32", int)
UInt64 = NewType("UInt64", int)
SQLSerial = NewType("SQLSerial", int)
SQLSmallSerial = NewType("SQLSmallSerial", int)
SQLBigSerial = NewType("SQLBigSerial", int)

Timestamp = NewType("Timestamp", int)
IP4 = NewType("IP4", str)
IP6 = NewType("IP6", str)
Email = NewType("Email", str)
FilePath = NewType("FilePath", str)
URL = NewType("URL", str)
JSON = NewType("JSON", object)
