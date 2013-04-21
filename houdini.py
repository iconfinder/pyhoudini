import sys
import ctypes.util


if sys.version_info[0] < 3:
    string_type = unicode
    byte_type = str
else:
    string_type = str
    byte_type = byte


libpath = ctypes.util.find_library('houdini')
if not libpath:
    raise ImportError("Couldn't find libhoudini with ctypes.util.find_library")
_libhoudini = ctypes.CDLL(libpath)


class _GHBuffer(ctypes.Structure):
    _fields_ = [
        ('ptr', ctypes.c_char_p),
        ('asize', ctypes.c_size_t),
        ('size', ctypes.c_size_t),
    ]

    def __init__(self, initial_size=0):
        _libhoudini.gh_buf_init(ctypes.byref(self),
                                ctypes.c_size_t(initial_size))

    def __str__(self):
        return self.ptr[:self.size]


def escaper(etype):
    gh_pointer = ctypes.POINTER(_GHBuffer)
    escaper_func = getattr(_libhoudini, 'houdini_' + etype)
    escaper_func.argtypes = [gh_pointer, ctypes.c_char_p, ctypes.c_size_t]

    def escape(string):
        is_string = isinstance(string, string_type)
        encoded = string.encode('utf-8') if is_string else string
        src = ctypes.c_char_p(encoded)
        size = ctypes.c_size_t(len(encoded))
        output_buffer = _GHBuffer()
        res = escaper_func(ctypes.byref(output_buffer), src, size)
        if not res:
            return string
        output_bytes = byte_type(output_buffer)
        return output_bytes.decode('utf-8') if is_string else output_bytes

    escape.__name__ = etype
    return escape


escape_html = escaper('escape_html')
unescape_html = escaper('unescape_html')
escape_xml = escaper('escape_xml')
escape_uri = escaper('escape_uri')
escape_url = escaper('escape_url')
escape_href = escaper('escape_href')
unescape_uri = escaper('unescape_uri')
unescape_url = escaper('unescape_url')
escape_js = escaper('escape_js')
unescape_js = escaper('unescape_js')
