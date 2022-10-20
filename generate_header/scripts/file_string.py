#-----------------------------------------------------------------------------
# This file is part of a Steinberg SDK. It is subject to the license terms
# in the LICENSE file found in the top-level directory of this distribution
# and at www.steinberg.net/sdklicenses. 
# No part of the SDK, including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.
#-----------------------------------------------------------------------------

class FileString(str):
    def __new__(cls, content=''):
        return super().__new__(cls, content)

    def __truediv__(self, key):
        return FileString(self + key + '\n')
