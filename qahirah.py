"""A Python 3 wrapper for the Cairo graphics library <http://cairographics.org/>
using ctypes. This is modelled on Pycairo, but differs from that in
some important ways. It also operates at a higher level than the underlying
Cairo API where this makes sense. For example, it defines a “Vector”
class for representing a 2D point, with operations on the Vector as a
whole, rather than having to operate on individual x- and y-coordinates.
Also, get/set API calls are collapsed into read/write Python properties
where this makes sense; for example, instead of Context.get_line_width()
and Context.set_line_width() calls, there is a Context.line_width property
that may be read and written.
"""
#+
# Copyright 2015 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import math
from numbers import \
    Number
import colorsys
import array
import ctypes as ct

cairo = ct.cdll.LoadLibrary("libcairo.so.2")
libc = ct.cdll.LoadLibrary("libc.so.6")
ft = ct.cdll.LoadLibrary("libfreetype.so.6")
try :
    fc = ct.cdll.LoadLibrary("libfontconfig.so.1")
except OSError as fail :
    if True : # if fail.errno == 2 : # ENOENT
      # no point checking, because it is None! (Bug?)
        fc = None
    else :
        raise
    #end if
#end try

class CAIRO :
    "useful definitions adapted from cairo.h. You will need to use the constants," \
    " but apart from that, see the more Pythonic wrappers defined outside this" \
    " class in preference to accessing low-level structures directly."

    # General ctypes gotcha: when passing addresses of ctypes-constructed objects
    # to routine calls, do not construct the objects directly in the call. Otherwise
    # the refcount goes to 0 before the routine is actually entered, and the object
    # can get prematurely disposed. Always store the object reference into a local
    # variable, and pass the value of the variable instead.

    status_t = ct.c_uint

    # cairo_status_t codes
    STATUS_SUCCESS = 0

    STATUS_NO_MEMORY = 1
    STATUS_INVALID_RESTORE = 2
    STATUS_INVALID_POP_GROUP = 3
    STATUS_NO_CURRENT_POINT = 4
    STATUS_INVALID_MATRIX = 5
    STATUS_INVALID_STATUS = 6
    STATUS_NULL_POINTER = 7
    STATUS_INVALID_STRING = 8
    STATUS_INVALID_PATH_DATA = 9
    STATUS_READ_ERROR = 10
    STATUS_WRITE_ERROR = 11
    STATUS_SURFACE_FINISHED = 12
    STATUS_SURFACE_TYPE_MISMATCH = 13
    STATUS_PATTERN_TYPE_MISMATCH = 14
    STATUS_INVALID_CONTENT = 15
    STATUS_INVALID_FORMAT = 16
    STATUS_INVALID_VISUAL = 17
    STATUS_FILE_NOT_FOUND = 18
    STATUS_INVALID_DASH = 19
    STATUS_INVALID_DSC_COMMENT = 20
    STATUS_INVALID_INDEX = 21
    STATUS_CLIP_NOT_REPRESENTABLE = 22
    STATUS_TEMP_FILE_ERROR = 23
    STATUS_INVALID_STRIDE = 24
    STATUS_FONT_TYPE_MISMATCH = 25
    STATUS_USER_FONT_IMMUTABLE = 26
    STATUS_USER_FONT_ERROR = 27
    STATUS_NEGATIVE_COUNT = 28
    STATUS_INVALID_CLUSTERS = 29
    STATUS_INVALID_SLANT = 30
    STATUS_INVALID_WEIGHT = 31
    STATUS_INVALID_SIZE = 32
    STATUS_USER_FONT_NOT_IMPLEMENTED = 33
    STATUS_DEVICE_TYPE_MISMATCH = 34
    STATUS_DEVICE_ERROR = 35
    STATUS_INVALID_MESH_CONSTRUCTION = 36
    STATUS_DEVICE_FINISHED = 37
    STATUS_JBIG2_GLOBAL_MISSING = 38

    STATUS_LAST_STATUS = 39

    # codes for cairo_surface_type_t
    SURFACE_TYPE_IMAGE = 0
    SURFACE_TYPE_PDF = 1
    SURFACE_TYPE_PS = 2
    SURFACE_TYPE_XLIB = 3
    SURFACE_TYPE_XCB = 4
    SURFACE_TYPE_GLITZ = 5
    SURFACE_TYPE_QUARTZ = 6
    SURFACE_TYPE_WIN32 = 7
    SURFACE_TYPE_BEOS = 8
    SURFACE_TYPE_DIRECTFB = 9
    SURFACE_TYPE_SVG = 10
    SURFACE_TYPE_OS2 = 11
    SURFACE_TYPE_WIN32_PRINTING = 12
    SURFACE_TYPE_QUARTZ_IMAGE = 13
    SURFACE_TYPE_SCRIPT = 14
    SURFACE_TYPE_QT = 15
    SURFACE_TYPE_RECORDING = 16
    SURFACE_TYPE_VG = 17
    SURFACE_TYPE_GL = 18
    SURFACE_TYPE_DRM = 19
    SURFACE_TYPE_TEE = 20
    SURFACE_TYPE_XML = 21
    SURFACE_TYPE_SKIA = 22
    SURFACE_TYPE_SUBSURFACE = 23
    SURFACE_TYPE_COGL = 24

    # cairo_format_t codes
    FORMAT_INVALID = -1
    FORMAT_ARGB32 = 0
    FORMAT_RGB24 = 1
    FORMAT_A8 = 2
    FORMAT_A1 = 3
    FORMAT_RGB16_565 = 4
    FORMAT_RGB30 = 5

    # cairo_content_t codes
    CONTENT_COLOR = 0x1000
    CONTENT_COLOUR = 0x1000
    CONTENT_ALPHA = 0x2000
    CONTENT_COLOR_ALPHA = 0x3000
    CONTENT_COLOUR_ALPHA = 0x3000

    # cairo_extend_t codes
    EXTEND_NONE = 0
    EXTEND_REPEAT = 1
    EXTEND_REFLECT = 2
    EXTEND_PAD = 3

    # cairo_filter_t codes
    FILTER_FAST = 0
    FILTER_GOOD = 1
    FILTER_BEST = 2
    FILTER_NEAREST = 3
    FILTER_BILINEAR = 4
    FILTER_GAUSSIAN = 5

    # cairo_operator_t codes
    OPERATOR_CLEAR = 0

    OPERATOR_SOURCE = 1
    OPERATOR_OVER = 2
    OPERATOR_IN = 3
    OPERATOR_OUT = 4
    OPERATOR_ATOP = 5

    OPERATOR_DEST = 6
    OPERATOR_DEST_OVER = 7
    OPERATOR_DEST_IN = 8
    OPERATOR_DEST_OUT = 9
    OPERATOR_DEST_ATOP = 10

    OPERATOR_XOR = 11
    OPERATOR_ADD = 12
    OPERATOR_SATURATE = 13

    OPERATOR_MULTIPLY = 14
    OPERATOR_SCREEN = 15
    OPERATOR_OVERLAY = 16
    OPERATOR_DARKEN = 17
    OPERATOR_LIGHTEN = 18
    OPERATOR_COLOR_DODGE = 19
    OPERATOR_COLOUR_DODGE = 19
    OPERATOR_COLOR_BURN = 20
    OPERATOR_COLOUR_BURN = 20
    OPERATOR_HARD_LIGHT = 21
    OPERATOR_SOFT_LIGHT = 22
    OPERATOR_DIFFERENCE = 23
    OPERATOR_EXCLUSION = 24
    OPERATOR_HSL_HUE = 25
    OPERATOR_HSL_SATURATION = 26
    OPERATOR_HSL_COLOR = 27
    OPERATOR_HSL_COLOUR = 27
    OPERATOR_HSL_LUMINOSITY = 28

    class matrix_t(ct.Structure) :
        _fields_ = \
            [
                ("xx", ct.c_double),
                ("yx", ct.c_double),
                ("xy", ct.c_double),
                ("yy", ct.c_double),
                ("x0", ct.c_double),
                ("y0", ct.c_double),
            ]
    #end matrix_t

    # cairo_antialias_t codes
    ANTIALIAS_DEFAULT = 0
    # method
    ANTIALIAS_NONE = 1
    ANTIALIAS_GRAY = 2
    ANTIALIAS_SUBPIXEL = 3
    # hints
    ANTIALIAS_FAST = 4
    ANTIALIAS_GOOD = 5
    ANTIALIAS_BEST = 6

    # cairo_subpixel_order_t codes
    SUBPIXEL_ORDER_DEFAULT = 0
    SUBPIXEL_ORDER_RGB = 1
    SUBPIXEL_ORDER_BGR = 2
    SUBPIXEL_ORDER_VRGB = 3
    SUBPIXEL_ORDER_VBGR = 4

    # cairo_hint_style_t codes
    HINT_STYLE_DEFAULT = 0
    HINT_STYLE_NONE = 1
    HINT_STYLE_SLIGHT = 2
    HINT_STYLE_MEDIUM = 3
    HINT_STYLE_FULL = 4

    # cairo_hint_metrics_t codes
    HINT_METRICS_DEFAULT = 0
    HINT_METRICS_OFF = 1
    HINT_METRICS_ON = 2

    # cairo_fill_rule_t codes
    FILL_RULE_WINDING = 0
    FILL_RULE_EVEN_ODD = 1

    # cairo_line_cap_t codes
    LINE_CAP_BUTT = 0
    LINE_CAP_ROUND = 1
    LINE_CAP_SQUARE = 2

    # cairo_line_join_t codes
    LINE_JOIN_MITER = 0
    LINE_JOIN_ROUND = 1
    LINE_JOIN_BEVEL = 2

    # cairo_path_data_type_t codes
    PATH_MOVE_TO = 0
    PATH_LINE_TO = 1
    PATH_CURVE_TO = 2
    PATH_CLOSE_PATH = 3
    path_data_type_t = ct.c_uint

    class path_data_t(ct.Union) :

        class header_t(ct.Structure) :
            "followed by header_t.length point_t structs."
            _fields_ = \
                [
                    ("type", ct.c_uint), # path_data_type_t
                    ("length", ct.c_int), # number of following points
                ]
        #end header_t
        header_ptr_t = ct.POINTER(header_t)

        class point_t(ct.Structure) :
            _fields_ = \
                [
                    ("x", ct.c_double),
                    ("y", ct.c_double),
                ]
        #end point_t
        point_ptr_t = ct.POINTER(point_t)

        _fields_ = \
            [
                ("header", header_t),
                ("point" , point_t),
            ]

    #end path_data_t
    path_data_t_ptr = ct.POINTER(path_data_t)

    class path_t(ct.Structure) :
        pass
    path_t._fields_ = \
        [
            ("status", status_t),
            ("data", ct.c_void_p), # path_data_t_ptr
            ("num_data", ct.c_int), # number of elements in data
        ]
    #end path_t
    path_ptr_t = ct.POINTER(path_t)

    class rectangle_t(ct.Structure) :
        _fields_ = \
            [
                ("x", ct.c_double),
                ("y", ct.c_double),
                ("width", ct.c_double),
                ("height", ct.c_double),
            ]
    #end rectangle_t
    rectangle_ptr_t = ct.POINTER(rectangle_t)

    class rectangle_list_t(ct.Structure) :
        pass
    rectangle_list_t._fields_ = \
        [
            ("status", status_t),
            ("rectangles", rectangle_ptr_t),
            ("num_rectangles", ct.c_int),
        ]
    #end rectangle_list_t
    rectangle_list_ptr_t = ct.POINTER(rectangle_list_t)

    class glyph_t(ct.Structure) :
        _fields_ = \
            [
                ("index", ct.c_ulong), # glyph index
                ("x", ct.c_double), # position relative to origin
                ("y", ct.c_double),
            ]
    #end glyph_t

    # cairo_font_type_t codes
    FONT_TYPE_TOY = 0
    FONT_TYPE_FT = 1
    FONT_TYPE_WIN32 = 2
    FONT_TYPE_QUARTZ = 3
    FONT_TYPE_USER = 4

    destroy_func_t = ct.CFUNCTYPE(None, ct.c_void_p)

    class font_extents_t(ct.Structure) :
        _fields_ = \
            [
                ("ascent", ct.c_double),
                ("descent", ct.c_double),
                ("height", ct.c_double),
                ("max_x_advance", ct.c_double),
                ("max_y_advance", ct.c_double),
            ]
    #end font_extents_t

    class text_extents_t(ct.Structure) :
        _fields_ = \
            [
                ("x_bearing", ct.c_double),
                ("y_bearing", ct.c_double),
                ("width", ct.c_double),
                ("height", ct.c_double),
                ("x_advance", ct.c_double),
                ("y_advance", ct.c_double),
            ]
    #end text_extents_t

    # codes for cairo_font_slant_t
    FONT_SLANT_NORMAL = 0
    FONT_SLANT_ITALIC = 1
    FONT_SLANT_OBLIQUE = 2

    # codes for cairo_font_weight_t
    FONT_WEIGHT_NORMAL = 0
    FONT_WEIGHT_BOLD = 1

    read_func_t = ct.CFUNCTYPE(ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_uint)
    write_func_t = ct.CFUNCTYPE(ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_uint)

    # codes for cairo_pdf_version_t
    PDF_VERSION_1_4 = 0
    PDF_VERSION_1_5 = 1

    # cairo_ps_level_t
    PS_LEVEL_2 = 0
    PS_LEVEL_3 = 3

    # codes for cairo_svg_version_t
    SVG_VERSION_1_1 = 0
    SVG_VERSION_1_2 = 1

    # codes for cairo_device_type_t
    DEVICE_TYPE_DRM = 0
    DEVICE_TYPE_GL = 1
    DEVICE_TYPE_SCRIPT = 2
    DEVICE_TYPE_XCB = 3
    DEVICE_TYPE_XLIB = 4
    DEVICE_TYPE_XML = 5
    DEVICE_TYPE_COGL = 6
    DEVICE_TYPE_WIN32 = 7
    DEVICE_TYPE_INVALID = -1

    # codes for cairo_script_mode_t
    SCRIPT_MODE_ASCII = 0
    SCRIPT_MODE_BINARY = 1

#end CAIRO

class HAS :
    "functionality queries. These are implemented by checking for the presence" \
    " of particular Cairo functions."
    pass # filled in below
#end HAS
for \
    symname, funcname \
in \
    (
        ("FC_FONT", "ft_font_face_create_for_ft_face"),
        ("FT_FONT", "ft_font_face_create_for_pattern"),
        ("IMAGE_SURFACE", "image_surface_create"),
        # TODO: MIME_SURFACE, OBSERVER_SURFACE?
        ("PDF_SURFACE", "pdf_surface_create"),
        ("PNG_FUNCTIONS", "surface_write_to_png"),
        ("PS_SURFACE", "ps_surface_create"),
        ("RECORDING_SURFACE", "recording_surface_create"),
        ("SCRIPT_SURFACE", "script_create"),
        ("SVG_SURFACE", "svg_surface_create"),
        # TODO: USER_FONT
    ) \
:
    setattr \
      (
        HAS,
        symname,
        hasattr(cairo, "cairo_" + funcname)
      )
#end for
del symname, funcname

def def_struct_class(name, ctname) :
    # defines a class with attributes that are a straightforward mapping
    # of a ctypes struct.

    ctstruct = getattr(CAIRO, ctname)

    class result_class :

        __slots__ = tuple(field[0] for field in ctstruct._fields_) # to forestall typos

        def to_cairo(self) :
            "returns a Cairo representation of the structure."
            result = ctstruct()
            for name, cttype in ctstruct._fields_ :
                setattr(result, name, getattr(self, name))
            #end for
            return \
                result
        #end to_cairo

        @staticmethod
        def from_cairo(r) :
            "decodes the Cairo representation of the structure."
            result = result_class()
            for name, cttype in ctstruct._fields_ :
                setattr(result, name, getattr(r, name))
            #end for
            return \
                result
        #end from_cairo

        def __getitem__(self, i) :
            "allows the object to be coerced to a tuple."
            return \
                getattr(self, ctstruct._fields_[i][0])
        #end __getitem__

        def __repr__(self) :
            return \
                (
                    "%s(%s)"
                %
                    (
                        name,
                        ", ".join
                          (
                            "%s = %s" % (field[0], getattr(self, field[0]))
                            for field in ctstruct._fields_
                          ),
                    )
                )
        #end __repr__

    #end result_class

#begin def_struct_class
    result_class.__name__ = name
    result_class.__doc__ = \
        (
            "representation of a Cairo %s structure. Fields are %s."
            "\nCreate by decoding the Cairo form with the from_cairo method;"
            " convert an instance to Cairo form with the to_cairo method."
        %
            (
                ctname,
                ", ".join(f[0] for f in ctstruct._fields_),
            )
        )
    return \
        result_class
#end def_struct_class

#+
# Routine arg/result types
#-

cairo.cairo_version_string.restype = ct.c_char_p
cairo.cairo_status_to_string.restype = ct.c_char_p

cairo.cairo_status.argtypes = (ct.c_void_p,)
cairo.cairo_create.argtypes = (ct.c_void_p,)
cairo.cairo_create.restype = ct.c_void_p
cairo.cairo_destroy.restype = ct.c_void_p
cairo.cairo_save.argtypes = (ct.c_void_p,)
cairo.cairo_restore.argtypes = (ct.c_void_p,)
cairo.cairo_get_target.restype = ct.c_void_p
cairo.cairo_get_target.argtypes = (ct.c_void_p,)
cairo.cairo_push_group.argtypes = (ct.c_void_p,)
cairo.cairo_push_group_with_content.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pop_group.restype = ct.c_void_p
cairo.cairo_pop_group.argtypes = (ct.c_void_p,)
cairo.cairo_pop_group_to_source.argtypes = (ct.c_void_p,)
cairo.cairo_get_group_target.restype = ct.c_void_p
cairo.cairo_get_group_target.argtypes = (ct.c_void_p,)

cairo.cairo_copy_path.argtypes = (ct.c_void_p,)
cairo.cairo_copy_path.restype = ct.c_void_p
cairo.cairo_copy_path_flat.argtypes = (ct.c_void_p,)
cairo.cairo_copy_path_flat.restype = ct.c_void_p
cairo.cairo_append_path.argtypes = (ct.c_void_p, ct.c_void_p) # not used
cairo.cairo_has_current_point.argtypes = (ct.c_void_p,)
cairo.cairo_get_current_point.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_new_path.argtypes = (ct.c_void_p,)
cairo.cairo_new_sub_path.argtypes = (ct.c_void_p,)
cairo.cairo_close_path.argtypes = (ct.c_void_p,)
cairo.cairo_arc.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_arc_negative.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_curve_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_line_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_move_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rectangle.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_glyph_path.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)
cairo.cairo_text_path.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_rel_curve_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_rel_line_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rel_move_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_path_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)

cairo.cairo_translate.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_scale.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rotate.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_transform.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_set_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_identity_matrix.argtypes = (ct.c_void_p,)
cairo.cairo_user_to_device.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_user_to_device_distance.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_device_to_user.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_device_to_user_distance.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)

cairo.cairo_get_source.argtypes = (ct.c_void_p,)
cairo.cairo_get_source.restype = ct.c_void_p
cairo.cairo_set_source_rgb.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double) # not used
cairo.cairo_set_source_rgba.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_set_source.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_antialias.argtypes = (ct.c_void_p,)
cairo.cairo_set_dash.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_double)
cairo.cairo_get_dash_count.argtypes = (ct.c_void_p,)
cairo.cairo_get_dash.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_set_antialias.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_set_fill_rule.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_fill_rule.argtypes = (ct.c_void_p,)
cairo.cairo_set_line_cap.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_line_cap.argtypes = (ct.c_void_p,)
cairo.cairo_set_line_join.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_line_join.argtypes = (ct.c_void_p,)
cairo.cairo_get_line_width.argtypes = (ct.c_void_p,)
cairo.cairo_get_line_width.restype = ct.c_double
cairo.cairo_set_line_width.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_get_miter_limit.restype = ct.c_double
cairo.cairo_set_miter_limit.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_get_operator.argtypes = (ct.c_void_p,)
cairo.cairo_set_operator.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_tolerance.restype = ct.c_double
cairo.cairo_set_tolerance.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_clip.argtypes = (ct.c_void_p,)
cairo.cairo_clip_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_clip_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_clip.restype = ct.c_bool
cairo.cairo_in_clip.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_copy_clip_rectangle_list.restype = CAIRO.rectangle_list_ptr_t
cairo.cairo_copy_clip_rectangle_list.argtypes = (ct.c_void_p,)
cairo.cairo_rectangle_list_destroy.argtypes = (CAIRO.rectangle_list_ptr_t,)
cairo.cairo_reset_clip.argtypes = (ct.c_void_p,)
cairo.cairo_fill.argtypes = (ct.c_void_p,)
cairo.cairo_fill_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_fill_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_fill.restype = ct.c_bool
cairo.cairo_in_fill.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_mask.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_mask_surface.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_paint.argtypes = (ct.c_void_p,)
cairo.cairo_paint_with_alpha.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_stroke.argtypes = (ct.c_void_p,)
cairo.cairo_stroke_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_stroke_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_stroke.restype = ct.c_bool
cairo.cairo_in_stroke.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_copy_page.argtypes = (ct.c_void_p,)
cairo.cairo_show_page.argtypes = (ct.c_void_p,)

cairo.cairo_path_destroy.argtypes = (ct.c_void_p,)

cairo.cairo_select_font_face.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_int, ct.c_int)
cairo.cairo_set_font_size.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_set_font_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_font_matrix.argtypes = (ct.c_void_p,)
cairo.cairo_get_font_matrix.restype = ct.c_void_p
cairo.cairo_set_font_options.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_font_options.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_set_font_face.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_font_face.restype = ct.c_void_p
cairo.cairo_get_font_face.argtypes = (ct.c_void_p,)
cairo.cairo_set_scaled_font.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_scaled_font.restype = ct.c_void_p
cairo.cairo_get_scaled_font.argtypes = (ct.c_void_p,)
cairo.cairo_show_text.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_show_glyphs.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_font_extents.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_text_extents.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p)
cairo.cairo_glyph_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_void_p)

cairo.cairo_surface_status.argtypes = (ct.c_void_p,)
cairo.cairo_surface_get_type.argtypes = (ct.c_void_p,)
cairo.cairo_surface_create_similar.restype = ct.c_void_p
cairo.cairo_surface_create_similar.argtypes = (ct.c_void_p, ct.c_int, ct.c_int, ct.c_int)
cairo.cairo_surface_create_similar_image.restype = ct.c_void_p
cairo.cairo_surface_create_similar_image.argtypes = (ct.c_void_p, ct.c_int, ct.c_int, ct.c_int)
cairo.cairo_surface_create_for_rectangle.restype = ct.c_void_p
cairo.cairo_surface_create_for_rectangle.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_surface_reference.restype = ct.c_void_p
cairo.cairo_surface_reference.argtypes = (ct.c_void_p,)
cairo.cairo_surface_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_surface_flush.argtypes = (ct.c_void_p,)
cairo.cairo_surface_get_device.restype = ct.c_void_p
cairo.cairo_surface_get_device.argtypes = (ct.c_void_p,)
cairo.cairo_surface_get_font_options.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_surface_get_content.restype = ct.c_int
cairo.cairo_surface_get_content.argtypes = (ct.c_void_p,)
cairo.cairo_surface_write_to_png.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_surface_write_to_png_stream.argtypes = (ct.c_void_p, CAIRO.write_func_t, ct.c_void_p)
cairo.cairo_surface_copy_page.argtypes = (ct.c_void_p,)
cairo.cairo_surface_show_page.argtypes = (ct.c_void_p,)

cairo.cairo_image_surface_create.restype = ct.c_void_p
cairo.cairo_image_surface_create_from_png.restype = ct.c_void_p
cairo.cairo_image_surface_create_from_png_stream.restype = ct.c_void_p
cairo.cairo_image_surface_create_from_png_stream.argtypes = (CAIRO.read_func_t, ct.c_void_p)
cairo.cairo_image_surface_create_for_data.restype = ct.c_void_p
cairo.cairo_image_surface_create_for_data.argtypes = (ct.c_void_p, ct.c_int, ct.c_int, ct.c_int, ct.c_int)
cairo.cairo_image_surface_get_format.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_width.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_height.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_stride.argtypes = (ct.c_void_p,)

cairo.cairo_pdf_surface_create.restype = ct.c_void_p
cairo.cairo_pdf_surface_create.argtypes = (ct.c_char_p, ct.c_double, ct.c_double)
cairo.cairo_pdf_surface_create_for_stream.restype = ct.c_void_p
cairo.cairo_pdf_surface_create_for_stream.argtypes = (CAIRO.write_func_t, ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_pdf_surface_restrict_to_version.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pdf_get_versions.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pdf_version_to_string.restype = ct.c_char_p
cairo.cairo_pdf_version_to_string.argtypes = (ct.c_int,)
cairo.cairo_pdf_surface_set_size.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_ps_surface_create.restype = ct.c_void_p
cairo.cairo_ps_surface_create.argtypes = (ct.c_char_p, ct.c_double, ct.c_double)
cairo.cairo_ps_surface_create_for_stream.restype = ct.c_void_p
cairo.cairo_ps_surface_create_for_stream.argtypes = (CAIRO.write_func_t, ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_ps_surface_restrict_to_level.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_ps_get_levels.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_ps_level_to_string.restype = ct.c_char_p
cairo.cairo_ps_level_to_string.argtypes = (ct.c_int,)
cairo.cairo_ps_surface_set_eps.argtypes = (ct.c_void_p, ct.c_bool)
cairo.cairo_ps_surface_get_eps.restype = ct.c_bool
cairo.cairo_ps_surface_get_eps.argtypes = (ct.c_void_p,)
cairo.cairo_ps_surface_set_size.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_ps_surface_dsc_begin_setup.argtypes = (ct.c_void_p,)
cairo.cairo_ps_surface_dsc_begin_page_setup.argtypes = (ct.c_void_p,)
cairo.cairo_ps_surface_dsc_comment.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_svg_surface_create.restype = ct.c_void_p
cairo.cairo_svg_surface_create.argtypes = (ct.c_char_p, ct.c_double, ct.c_double)
cairo.cairo_svg_surface_create_for_stream.restype = ct.c_void_p
cairo.cairo_svg_surface_create_for_stream.argtypes = (CAIRO.write_func_t, ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_svg_surface_restrict_to_version.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_svg_get_versions.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_svg_version_to_string.restype = ct.c_char_p
cairo.cairo_svg_version_to_string.argtypes = (ct.c_int,)
cairo.cairo_recording_surface_create.restype = ct.c_void_p
cairo.cairo_recording_surface_create.argtypes = (ct.c_int, ct.c_void_p)
cairo.cairo_recording_surface_ink_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_recording_surface_get_extents.restype = ct.c_bool
cairo.cairo_recording_surface_get_extents.argtypes = (ct.c_void_p, ct.c_void_p)

cairo.cairo_device_status.argtypes = (ct.c_void_p,)
cairo.cairo_device_get_type.argtypes = (ct.c_void_p,)

cairo.cairo_script_create.restype = ct.c_void_p
cairo.cairo_script_create.argtypes = (ct.c_char_p,)
cairo.cairo_script_create_for_stream.restype = ct.c_void_p
cairo.cairo_script_create_for_stream.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_script_from_recording_surface.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_script_get_mode.restype = ct.c_int
cairo.cairo_script_get_mode.argtypes = (ct.c_void_p,)
cairo.cairo_script_set_mode.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_script_surface_create.restype = ct.c_int
cairo.cairo_script_surface_create.argtypes = (ct.c_void_p, ct.c_int, ct.c_double, ct.c_double)
cairo.cairo_script_surface_create_for_target.restype = ct.c_int
cairo.cairo_script_surface_create_for_target.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_script_write_comment.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)

cairo.cairo_pattern_status.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_reference.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_reference.restype = ct.c_void_p
cairo.cairo_pattern_add_color_stop_rgb.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double) # not used
cairo.cairo_pattern_add_color_stop_rgba.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_get_color_stop_count.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_color_stop_rgba.argtypes = (ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_rgb.argtypes = (ct.c_double, ct.c_double, ct.c_double) # not used
cairo.cairo_pattern_create_rgb.restype = ct.c_void_p # not used
cairo.cairo_pattern_create_rgba.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_create_rgba.restype = ct.c_void_p
cairo.cairo_pattern_get_rgba.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_for_surface.restype = ct.c_void_p
cairo.cairo_pattern_create_for_surface.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_create_linear.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_create_linear.restype = ct.c_void_p
cairo.cairo_pattern_get_linear_points.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_radial.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_get_radial_circles.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_extend.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_set_extend.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pattern_get_filter.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_set_filter.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pattern_get_surface.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_set_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_mesh.restype = ct.c_void_p
cairo.cairo_mesh_pattern_begin_patch.argtypes = (ct.c_void_p,)
cairo.cairo_mesh_pattern_end_patch.argtypes = (ct.c_void_p,)
cairo.cairo_mesh_pattern_move_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_mesh_pattern_line_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_mesh_pattern_curve_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_mesh_pattern_set_control_point.argtypes = (ct.c_void_p, ct.c_uint, ct.c_double, ct.c_double)
cairo.cairo_mesh_pattern_set_corner_color_rgb.argtypes = (ct.c_void_p, ct.c_uint, ct.c_double, ct.c_double, ct.c_double) # not used
cairo.cairo_mesh_pattern_set_corner_color_rgba.argtypes = (ct.c_void_p, ct.c_uint, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_mesh_pattern_get_patch_count.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_mesh_pattern_get_path.restype = ct.c_void_p
cairo.cairo_mesh_pattern_get_path.argtypes = (ct.c_void_p, ct.c_uint)
cairo.cairo_mesh_pattern_get_control_point.argtypes = (ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_void_p, ct.c_void_p)
cairo.cairo_mesh_pattern_get_corner_color_rgba.argtypes = (ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)

cairo.cairo_font_options_status.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_create.restype = ct.c_void_p
cairo.cairo_font_options_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_copy.restype = ct.c_void_p
cairo.cairo_font_options_copy.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_merge.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_font_options_equal.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_font_options_equal.restype = ct.c_bool
cairo.cairo_font_options_get_antialias.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_antialias.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_subpixel_order.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_subpixel_order.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_hint_style.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_hint_style.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_hint_metrics.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_hint_metrics.argtypes = (ct.c_void_p, ct.c_int)

cairo.cairo_font_face_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_font_face_status.argtypes = (ct.c_void_p,)
cairo.cairo_font_face_get_type.argtypes = (ct.c_void_p,)
cairo.cairo_font_face_set_user_data.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_toy_font_face_create.argtypes = (ct.c_char_p, ct.c_int, ct.c_int)
cairo.cairo_toy_font_face_create.restype = ct.c_void_p
cairo.cairo_toy_font_face_get_family.argtypes = (ct.c_void_p,)
cairo.cairo_toy_font_face_get_family.restype = ct.c_char_p
cairo.cairo_toy_font_face_get_slant.argtypes = (ct.c_void_p,)
cairo.cairo_toy_font_face_get_weight.argtypes = (ct.c_void_p,)
cairo.cairo_ft_font_face_create_for_ft_face.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_ft_font_face_create_for_ft_face.restype = ct.c_void_p
cairo.cairo_ft_font_face_create_for_pattern.argtypes = (ct.c_void_p,)
cairo.cairo_ft_font_face_create_for_pattern.restype = ct.c_void_p
cairo.cairo_ft_font_options_substitute.argtypes = (ct.c_void_p, ct.c_void_p)

cairo.cairo_scaled_font_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_scaled_font_status.argtypes = (ct.c_void_p,)
cairo.cairo_scaled_font_create.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_extents.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_text_extents.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p)
cairo.cairo_scaled_font_glyph_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_void_p)
cairo.cairo_scaled_font_get_font_face.restype = ct.c_void_p
cairo.cairo_scaled_font_get_font_face.argtypes = (ct.c_void_p,)
cairo.cairo_scaled_font_get_font_options.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_get_font_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_get_ctm.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_get_scale_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_scaled_font_get_type.argtypes = (ct.c_void_p,)

libc.memcpy.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_size_t)

if fc != None :
    fc.FcInit.restype = ct.c_bool
    fc.FcNameParse.argtypes = (ct.c_char_p,)
    fc.FcNameParse.restype = ct.c_void_p
    fc.FcConfigSubstitute.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)
    fc.FcConfigSubstitute.restype = ct.c_bool
    fc.FcDefaultSubstitute.argtypes = (ct.c_void_p,)
    fc.FcDefaultSubstitute.restype = None
    fc.FcPatternDestroy.argtypes = (ct.c_void_p,)
    fc.FcPatternDestroy.restype = None

    class _FC :
        # minimal Fontconfig interface, just sufficient for my needs.

        FcMatchPattern = 0
        FcResultMatch = 0

    #end _FC

    class _FcPatternManager :
        # context manager which collects a list of FcPattern objects requiring disposal.

        def __init__(self) :
            self.to_dispose = []
        #end __init__

        def __enter__(self) :
            return \
                self
        #end __enter__

        def collect(self, pattern) :
            "collects another FcPattern reference to be disposed."
            # c_void_p function results are peculiar: they return integers
            # for non-null values, but None for null.
            if pattern != None :
                self.to_dispose.append(pattern)
            #end if
            return \
                pattern
        #end collect

        def __exit__(self, exception_type, exception_value, traceback) :
            for pattern in self.to_dispose :
                fc.FcPatternDestroy(pattern)
            #end for
        #end __exit__

    #end _FcPatternManager

#end if

ft_lib = None
ft_destroy_key = ct.c_int() # dummy address

def _ensure_ft() :
    # ensures FreeType is usable, raising suitable exceptions if not.
    global ft_lib
    if ft_lib == None :
        lib = ct.c_void_p()
        status = ft.FT_Init_FreeType(ct.byref(lib))
        if status != 0 :
            raise RuntimeError("Error %d initializing FreeType" % status)
        #end if
        ft_lib = lib.value
    #end if
#end _ensure_ft

fc_inited = False

def _ensure_fc() :
    # ensures Fontconfig is usable, raising suitable exceptions if not.
    global fc_inited
    if not fc_inited :
        if fc == None :
            raise NotImplementedError("Fontconfig not available")
        #end if
        if not fc.FcInit() :
            raise RuntimeError("failed to initialize Fontconfig.")
        #end if
        fc_inited = True
    #end if
#end _ensure_fc

#+
# Higher-level stuff begins here
#-

def version() :
    "returns the Cairo version as a single integer."
    return \
        cairo.cairo_version()
#end version

def version_tuple() :
    "returns the Cairo version as a triple of integers."
    vers = cairo.cairo_version()
    return \
        (vers // 10000, vers // 100 % 100, vers % 100)
#end version_tuple

def version_string() :
    "returns the Cairo version string."
    return \
        cairo.cairo_version_string().decode("utf-8")
#end version_string

def status_to_string(status) :
    "returns the message for a given Cairo status code."
    return \
        cairo.cairo_status_to_string(status).decode("utf-8")
#end status_to_string

def debug_reset_static_data() :
    cairo.cairo_debug_reset_static_data()
#end debug_reset_static_data

def check(status) :
    "checks status for success, raising a CairoError if not."
    if status != 0 :
        raise CairoError(status)
    #end if
#end check

class CairoError(Exception) :
    "just to identify a Cairo-specific error exception."

    def __init__(self, code) :
        self.args = ("Cairo error %d -- %s" % (code, status_to_string(code)),)
    #end __init__

#end CairoError

deg = 180 / math.pi
  # All angles are in radians. You can use the standard Python functions math.degrees
  # and math.radians to convert back and forth, or multiply and divide by this deg
  # factor: divide by deg to convert degrees to radians, and multiply by deg to convert
  # the other way, e.g.
  #
  #     math.sin(45 / deg)
  #     math.atan(1) * deg

class Vector :
    "something missing from Cairo itself, a representation of a 2D point."

    __slots__ = ("x", "y") # to forestall typos

    def __init__(self, x, y) :
        self.x = x
        self.y = y
    #end __init__

    @staticmethod
    def from_tuple(v) :
        "converts a tuple of 2 numbers to a Vector. Can be used to ensure that" \
        " v is a Vector."
        return \
            Vector(*v)
    #end from_tuple

    def __repr__(self) :
        return \
            (
                "Vector(%%%(fmt)s, %%%(fmt)s)"
            %
                {"fmt" : (".3f", "d")[isinstance(self.x, int) and isinstance(self.y, int)]}
            %
                (self.x, self.y)
            )
    #end __repr__

    def __getitem__(self, i) :
        "being able to access elements by index allows a Vector to be cast to a tuple or list."
        return \
            (self.x, self.y)[i]
    #end __getitem__

    def __eq__(v1, v2) :
        "equality of two Vectors."
        return \
            (
                isinstance(v2, Vector)
            and
                v1.x == v2.x
            and
                v1.y == v2.y
            )
    #end __eq__

    def __add__(v1, v2) :
        "offset one Vector by another."
        return \
            (
                lambda : NotImplemented,
                lambda : Vector(v1.x + v2.x, v1.y + v2.y)
            )[isinstance(v2, Vector)]()
    #end __add__

    def __neg__(self) :
        "reflect across origin."
        return Vector \
          (
            x = - self.x,
            y = - self.y
          )
    #end __neg__

    def __sub__(v1, v2) :
        "difference between two Vectors."
        return \
            (
                lambda : NotImplemented,
                lambda : Vector(v1.x - v2.x, v1.y - v2.y)
            )[isinstance(v2, Vector)]()
    #end __sub__

    def __mul__(v, f) :
        "scale a Vector uniformly by a number or non-uniformly by another Vector."
        if isinstance(f, Vector) :
            result = Vector(v.x * f.x, v.y * f.y)
        elif isinstance(f, Number) :
            result = Vector(v.x * f, v.y * f)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __mul__
    __rmul__ = __mul__

    def __truediv__(v, f) :
        "inverse-scale a Vector uniformly by a number or non-uniformly by another Vector."
        if isinstance(f, Vector) :
            result = Vector(v.x / f.x, v.y / f.y)
        elif isinstance(f, Number) :
            result = Vector(v.x / f, v.y / f)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __truediv__

    def __mod__(v, f) :
        "remainder on division of one Vector by another."
        if isinstance(f, Vector) :
            result = Vector(v.x % f.x, v.y % f.y)
        elif isinstance(f, Number) :
            result = Vector(v.x % f, v.y % f)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __mod__

    def __round__(self) :
        "returns the Vector with all coordinates rounded to integers."
        return \
            Vector(round(self.x), round(self.y))
    #end __round__

    @staticmethod
    def unit(angle) :
        "returns the unit vector with the specified direction."
        return \
            Vector(math.cos(angle), math.sin(angle))
    #end unit

    def rotate(self, angle) :
        "returns the Vector rotated by the specified angle."
        cos = math.cos(angle)
        sin = math.sin(angle)
        return \
            Vector(self.x * cos - self.y * sin, self.x * sin + self.y * cos)
    #end rotate

    def __abs__(self) :
        "use abs() to get the length of a Vector."
        return \
            math.hypot(self.x, self.y)
    #end __abs__

    def angle(self) :
        "returns the Vector’s rotation angle."
        return \
            math.atan2(self.y, self.x)
    #end angle

    @staticmethod
    def from_polar(length, angle) :
        "constructs a Vector from a length and a direction."
        return \
            Vector(length * math.cos(angle), length * math.sin(angle))
    #end from_polar

#end Vector
Vector.zero = Vector(0, 0)

class Matrix :
    "representation of a 3-by-2 affine homogeneous matrix. This does not" \
    " actually use any Cairo routines to implement its calculations; these" \
    " are done entirely using Python numerics. The from_cairo and to_cairo" \
    " methods provide conversion to/from cairo_matrix_t structs. Routines" \
    " elsewhere expect this Matrix type where the underlying Cairo routine" \
    " wants a cairo_matrix_t, and return this type where the Cairo routine" \
    " returns a cairo_matrix_t."

    __slots__ = ("xx", "yx", "xy", "yy", "x0", "y0") # to forestall typos

    def __init__(self, xx, yx, xy, yy, x0, y0) :
        self.xx = xx
        self.yx = yx
        self.xy = xy
        self.yy = yy
        self.x0 = x0
        self.y0 = y0
        # self.u = 0
        # self.v = 0
        # self.w = 1
    #end __init__

    @staticmethod
    def from_cairo(m) :
        return \
            Matrix(m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)
    #end from_cairo

    def to_cairo(m) :
        return \
            CAIRO.matrix_t(m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)
    #end to_cairo

    @staticmethod
    def identity() :
        "returns an identity matrix."
        return Matrix(1, 0, 0, 1, 0, 0)
    #end identity

    def __mul__(m1, m2) :
        "returns concatenation with another Matrix."
        return Matrix \
          (
            xx = m1.xx * m2.xx + m1.xy * m2.yx,
            yx = m1.yx * m2.xx + m1.yy * m2.yx,
            xy = m1.xx * m2.xy + m1.xy * m2.yy,
            yy = m1.yx * m2.xy + m1.yy * m2.yy,
            x0 = m1.xx * m2.x0 + m1.xy * m2.y0 + m1.x0,
            y0 = m1.yx * m2.x0 + m1.yy * m2.y0 + m1.y0,
          )
    #end __mul__

    def __pow__(m, p) :
        "raising of a Matrix to an integer power p is equivalent to applying" \
        " the transformation p times in succession."
        if isinstance(p, int) :
            if p < 0 :
                m = m.inv()
                p = -p
            #end if
            result = Matrix.identity()
            # O(N) exponentiation algorithm should be good enough for small
            # powers, not expecting large ones
            for i in range(p) :
                result *= m
            #end for
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __pow__

    @staticmethod
    def translate(delta) :
        "returns a Matrix that translates by the specified delta Vector."
        tx, ty = Vector.from_tuple(delta)
        return Matrix(1, 0, 0, 1, tx, ty)
    #end translate

    @staticmethod
    def scale(factor, centre = None) :
        "returns a Matrix that scales by the specified scalar or Vector factors" \
        " about Vector centre, or the origin if not specified."
        if isinstance(factor, Number) :
            result = Matrix(factor, 0, 0, factor, 0, 0)
        elif isinstance(factor, Vector) :
            result = Matrix(factor.x, 0, 0, factor.y, 0, 0)
        elif isinstance(factor, tuple) :
            sx, sy = factor
            result = Matrix(sx, 0, 0, sy, 0, 0)
        else :
            raise TypeError("factor must be a number or a Vector")
        #end if
        if centre != None :
            centre = Vector.from_tuple(centre)
            result = Matrix.translate(centre) * result * Matrix.translate(- centre)
        #end if
        return \
            result
    #end scale

    @staticmethod
    def rotate(angle, centre = None) :
        "returns a Matrix that rotates about the origin by the specified" \
        " angle in radians about Vector centre, or the origin if not specified."
        cos = math.cos(angle)
        sin = math.sin(angle)
        result = Matrix(cos, sin, -sin, cos, 0, 0)
        if centre != None :
            centre = Vector.from_tuple(centre)
            result = Matrix.translate(centre) * result * Matrix.translate(- centre)
        #end if
        return \
            result
    #end rotate

    @staticmethod
    def skew(vec, centre = None) :
        "returns a Matrix that skews by the specified vec.x and vec.y factors" \
        " about Vector centre, or the origin if not specified."
        sx, sy = Vector.from_tuple(vec)
        result = Matrix(1, sy, sx, 1, 0, 0)
        if centre != None :
            centre = Vector.from_tuple(centre)
            result = Matrix.translate(centre) * result * Matrix.translate(- centre)
        #end if
        return \
            result
    #end skew

    def det(self) :
        "matrix determinant."
        return \
            self.xx * self.yy - self.xy * self.yx
    #end det

    def adj(self) :
        "matrix adjoint."
        return Matrix \
          (
            xx = self.yy,
            yx = - self.yx,
            xy = - self.xy,
            yy = self.xx,
            x0 = self.xy * self.y0 - self.yy * self.x0,
            y0 = self.yx * self.x0 - self.xx * self.y0,
          )
    #end adj

    def inv(self) :
        "matrix inverse."
        # computed using minors <http://mathworld.wolfram.com/MatrixInverse.html>
        adj = self.adj()
        det = self.det()
        return Matrix \
          (
            xx = adj.xx / det,
            yx = adj.yx / det,
            xy = adj.xy / det,
            yy = adj.yy / det,
            x0 = adj.x0 / det,
            y0 = adj.y0 / det,
          )
    #end inv

    def map(self, pt) :
        "maps a Vector through the Matrix."
        x, y = Vector.from_tuple(pt)
        return Vector \
          (
            x = x * self.xx + y * self.xy + self.x0,
            y = x * self.yx + y * self.yy + self.y0
          )
    #end map

    def mapdelta(self, pt) :
        "maps a Vector through the Matrix, ignoring the translation part."
        x, y = Vector.from_tuple(pt)
        return Vector \
          (
            x = x * self.xx + y * self.xy,
            y = x * self.yx + y * self.yy
          )
    #end mapdelta

    def mapiter(self, pts) :
        "maps an iterable of Vectors through the Matrix."
        pts = iter(pts)
        while True : # until pts raises StopIteration
            yield self.map(next(pts))
        #end while
    #end mapiter

    def mapdeltaiter(self, pts) :
        "maps an iterable of Vectors through the Matrix, ignoring the" \
        " translation part."
        pts = iter(pts)
        while True : # until pts raises StopIteration
            yield self.mapdelta(next(pts))
        #end while
    #end mapdeltaiter

    def __repr__(self) :
        return \
            (
                "Matrix(%f, %f, %f, %f, %f, %f)"
            %
                (
                    self.xx, self.yx,
                    self.xy, self.yy,
                    self.x0, self.y0,
                )
            )
    #end __repr__

#end Matrix

def interp(fract, p1, p2) :
    "returns the point along p1 to p2 at relative position fract."
    return (p2 - p1) * fract + p1
#end interp

def distribute(nrdivs, p1 = 0.0, p2 = 1.0, endincl = False) :
    "returns a sequence of nrdivs values evenly distributed over" \
    " [p1, p2) (if not endincl) or nrdivs + 1 values over [p1, p2] (if endincl)."
    interval = p2 - p1
    return tuple \
      (
        interval * (i / nrdivs) + p1
            for i in range(0, nrdivs + int(endincl))
      )
#end distribute

class Rect :
    "an axis-aligned rectangle. The constructor takes the left and top coordinates," \
    " and the width and height. Or use from_corners to construct one from two Vectors" \
    " representing opposite corners, or from_dimensions to construct one from a Vector" \
    " giving the width and height, with the topleft set to (0, 0)."

    __slots__ = ("left", "top", "width", "height") # to forestall typos

    def __init__(self, left, top, width, height) :
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    #end __init__

    @staticmethod
    def from_corners(pt1, pt2) :
        "constructs a Rect from two opposite corner Vectors."
        pt1 = Vector.from_tuple(pt1)
        pt2 = Vector.from_tuple(pt2)
        min_x = min(pt1.x, pt2.x)
        max_x = max(pt1.x, pt2.x)
        min_y = min(pt1.y, pt2.y)
        max_y = max(pt1.y, pt2.y)
        return \
            Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    #end from_corners

    @staticmethod
    def from_dimensions(pt) :
        "a Rect with its top left at (0, 0) and the given width and height."
        pt = Vector.from_tuple(pt)
        return \
            Rect(0, 0, pt.x, pt.y)
    #end from_dimensions

    @staticmethod
    def from_cairo(r) :
        "converts a CAIRO.rectangle_t to a Rect."
        return \
            Rect(r.x, r.y, r.width, r.height)
    #end from_cairo

    def to_cairo(self) :
        "converts the Rect to a CAIRO.rectangle_t."
        return \
            CAIRO.rectangle_t(self.left, self.top, self.width, self.height)
    #end to_cairo

    @property
    def bottom(self) :
        "the bottom y-coordinate of the Rect."
        return \
            self.top + self.height
    #end bottom

    @property
    def right(self) :
        "the right x-coordinate of the Rect."
        return \
            self.left + self.width
    #end right

    @property
    def topleft(self) :
        "the top-left corner point."
        return \
            Vector(self.left, self.top)
    #end topleft

    @property
    def botright(self) :
        "the bottom-right corner point."
        return \
            Vector(self.left + self.width, self.top + self.height)
    #end botright

    @property
    def dimensions(self) :
        "the dimensions of the Rect as a Vector."
        return \
            Vector(self.width, self.height)
    #end dimensions

    @property
    def middle(self) :
        "the midpoint as a Vector."
        return \
            Vector(self.left + self.width / 2, self.top + self.height / 2)
    #end middle

    def __round__(self) :
        "returns the Rect with all coordinates rounded to integers."
        return \
            Rect(round(self.left), round(self.top), round(self.width), round(self.height))
    #end __round__

    def __add__(self, v) :
        "add a Rect to a Vector to return the Rect offset by the Vector."
        if isinstance(v, Vector) :
            result = Rect(self.left + v.x, self.top + v.y, self.width, self.height)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __add__

    def __sub__(self, v) :
        "subtract a Vector from a Rect to return the Rect offset in the" \
        " opposite direction to the Vector."
        if isinstance(v, Vector) :
            result = Rect(self.left - v.x, self.top - v.y, self.width, self.height)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __sub__

    def __eq__(r1, r2) :
        "equality of two rectangles."
        return \
            (
                isinstance(r2, Rect)
            and
                r1.left == r2.left
            and
                r1.top == r2.top
            and
                r1.width == r2.width
            and
                r1.height == r2.height
            )
    #end __eq__

    def __repr__(self) :
        return \
            (
                "Rect(%%%(fmt)s, %%%(fmt)s, %%%(fmt)s, %%%(fmt)s)"
            %
                {"fmt" :
                    (".3f", "d")
                    [
                        isinstance(self.left, int)
                    and
                        isinstance(self.top, int)
                    and
                        isinstance(self.width, int)
                    and
                        isinstance(self.height, int)
                    ]
                }
            %
                (self.left, self.top, self.width, self.height)
            )
    #end __repr__

    def inset(self, v) :
        "returns a Rect inset by the specified x and y amounts from this one" \
        " (use negative values to outset)."
        dx, dy = Vector.from_tuple(v)
        return \
            Rect(self.left + dx, self.top + dy, self.width - 2 * dx, self.height - 2 * dy)
    #end inset

    def position(self, relpt, halign = None, valign = None) :
        "returns a copy of this Rect repositioned relative to Vector relpt, horizontally" \
        " according to halign and vertically according to valign (if not None" \
        " in each case). halign = 0 means the left edge is on the point, while" \
        " halign = 1 means the right edge is on the point. Similarly valign = 0" \
        " means the top edge is on the point, while valign = 1 means the bottom" \
        " edge is on the point. Intermediate values correspond to intermediate" \
        " linearly-interpolated positions."
        left = self.left
        top = self.top
        if halign != None :
            left = relpt.x - interp(halign, 0, self.width)
        #end if
        if valign != None :
            top = relpt.y - interp(valign, 0, self.height)
        #end if
        return Rect(left = left, top = top, width = self.width, height = self.height)
    #end position

    def align(self, within, halign = None, valign = None) :
        "returns a copy of this Rect repositioned relative to within, which is" \
        " another Rect, horizontally according to halign and vertically according" \
        " to valign (if not None in each case). halign = 0 means the left edges" \
        " coincide, while halign = 1 means the right edges coincide. Similarly" \
        " valign = 0 means the top edges coincide, while valign = 1 means the" \
        " bottom edges coincide. Intermediate values correspond to intermediate" \
        " linearly-interpolated positions."
        left = self.left
        top = self.top
        if halign != None :
            left = interp(halign, within.left, within.left + within.width - self.width)
        #end if
        if valign != None :
            top = interp(valign, within.top, within.top + within.height - self.height)
        #end if
        return Rect(left = left, top = top, width = self.width, height = self.height)
    #end align

    def transform_to(src, dst) :
        "returns a Matrix which maps this Rect into dst Rect."
        return \
            (
                Matrix.translate(dst.topleft)
            *
                Matrix.scale(dst.dimensions / src.dimensions)
            *
                Matrix.translate(- src.topleft)
            )
    #end transform_to

    def fit_to(src, dst, outside = False) :
        "returns a Matrix which maps this Rect onto dst Rect without distortion" \
        " if the aspect ratios don’t match. Instead, src will be uniformly scaled" \
        " to the largest possible size that fits within dst if outside is False," \
        " or to the smallest possible size that dst will fit within if outside is" \
        " True."
        scale = dst.dimensions / src.dimensions
        scale = (min, max)[outside](scale.x, scale.y)
        return \
          (
                Matrix.translate(dst.middle)
            *
                Matrix.scale((scale, scale))
            *
                Matrix.translate(- src.middle)
          )
    #end fit_to

#end Rect

class Glyph :
    "specifies a glyph index and position relative to the origin."

    __slots__ = ("index", "pos") # to forestall typos

    def __init__(self, index, pos) :
        if not isinstance(pos, Vector) :
            raise TypeError("pos is not a Vector")
        #end if
        self.index = index
        self.pos = pos
    #end __init__

#end Glyph

def glyphs_to_cairo(glyphs) :
    "converts a sequence of Glyph objects to Cairo form."
    nr_glyphs = len(glyphs)
    buf = (nr_glyphs * CAIRO.glyph_t)()
    for i in range(nr_glyphs) :
        src = glyphs[i]
        buf[i] = CAIRO.glyph_t(src.index, src.pos.x, src.pos.y)
    #end for
    return \
        buf, nr_glyphs
#end glyphs_to_cairo

class Context :
    "a Cairo drawing context. Instantiate with a Surface object." \
    " Many methods return the context to allow method chaining."
    # <http://cairographics.org/manual/cairo-cairo-t.html>

    __slots__ = ("_cairobj", "_user_data") # to forestall typos

    def _check(self) :
        # check for error from last operation on this Context.
        check(cairo.cairo_status(self._cairobj))
    #end _check

    def __init__(self, surface) :
        self._cairobj = cairo.cairo_create(surface._cairobj)
        self._check()
        self._user_data = {}
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def save(self) :
        "saves the Cairo graphics state."
        cairo.cairo_save(self._cairobj)
        return \
            self
    #end save

    def restore(self) :
        "restores the last saved-but-not-restored graphics state."
        cairo.cairo_restore(self._cairobj)
        self._check()
        return \
            self
    #end restore

    @property
    def target(self) :
        "a copy of the current target Surface. Will not return the same" \
        " wrapper object each time, but Surface objects can be compared for equality," \
        " which means they reference the same underlying Cairo surface_t object."
        return \
            Surface(cairo.cairo_surface_reference(cairo.cairo_get_target(self._cairobj)))
    #end target

    def push_group(self) :
        "temporarily redirects drawing to a temporary surface with content" \
        " CAIRO.CONTENT_COLOUR_ALPHA."
        cairo.cairo_push_group(self._cairobj)
        return \
            self
    #end push_group

    def push_group_with_content(self, content) :
        "temporarily redirects drawing to a temporary surface. content is a CAIRO.CONTENT_xxx value."
        cairo.cairo_push_group_with_content(self._cairobj, content)
        return \
            self
    #end push_group_with_content

    def pop_group(self) :
        "pops the last pushed-but-not-popped group redirection, and returns a Pattern" \
        " containing the result of the redirected drawing."
        return \
            Pattern(cairo.cairo_pop_group(self._cairobj))
    #end pop_group

    def pop_group_to_source(self) :
        "pops the last pushed-but-not-popped group redirection, and sets the Pattern" \
        " containing the result of the redirected drawing as the Context.source."
        cairo.cairo_pop_group_to_source(self._cairobj)
        self._check()
        return \
            self
    #end pop_group_to_source

    @property
    def group_target(self) :
        "returns the current group redirection target, or the original Surface if no" \
        " redirection is in effect."
        return \
            Surface(cairo.cairo_surface_reference(cairo.cairo_get_group_target(self._cairobj)))
    #end group_target

    @property
    def source(self) :
        "a copy of the current source Pattern. Will not return the same" \
        " wrapper object each time, but Pattern objects can be compared for equality," \
        " which means they reference the same underlying Cairo pattern_t object."
        return \
            Pattern(cairo.cairo_pattern_reference(cairo.cairo_get_source(self._cairobj)))
    #end source

    @source.setter
    def source(self, source) :
        "the current source Pattern."
        self.set_source(source)
    #end source

    def set_source(self, source) :
        "sets a new source Pattern. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the source property."
        if not isinstance(source, Pattern) :
            raise TypeError("source is not a Pattern")
        #end if
        cairo.cairo_set_source(self._cairobj, source._cairobj)
        self._check()
        return \
            self
    #end set_source

    @property
    def source_colour(self) :
        "returns the current source pattern Colour. The current source Pattern must" \
        " be a plain-colour pattern."
        return \
            self.source.colour
    #end source_colour

    @source_colour.setter
    def source_colour(self, c) :
        self.set_source_colour(c)
    #end source_colour

    def set_source_colour(self, c) :
        "sets a new plain-colour pattern as the source. c must be a Colour" \
        " object or a tuple."
        cairo.cairo_set_source_rgba(*((self._cairobj,) + tuple(Colour.from_rgba(c))))
        self._check()
        return \
            self
    #end set_source_colour

    @property
    def antialias(self) :
        "the current antialias mode."
        return \
            cairo.cairo_get_antialias(self._cairobj)
    #end antialias

    @antialias.setter
    def antialias(self, antialias) :
        self.set_antialias(antialias)
    #end antialias

    def set_antialias(self, antialias) :
        "sets a new antialias mode. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the antialias property."
        cairo.cairo_set_antialias(self._cairobj, antialias)
        return \
            self
    #end set_antialias

    @property
    def dash(self) :
        "the current line dash setting, as a tuple of two items: the first is a tuple" \
        " of reals specifying alternating on- and off-lengths, the second is a real" \
        " specifying the starting offset."
        segs = (cairo.cairo_get_dash_count(self._cairobj) * ct.c_double)()
        offset = ct.c_double()
        cairo.cairo_get_dash(self._cairobj, ct.byref(segs), ct.byref(offset))
        return \
            (tuple(i for i in segs), offset.value)
    #end dash

    @dash.setter
    def dash(self, dashes) :
        self.set_dash(dashes)
    #end dash

    def set_dash(self, dashes) :
        "sets a new line dash. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the dash property."
        segs, offset = dashes
        nrsegs = len(segs)
        csegs = (nrsegs * ct.c_double)()
        for i in range(nrsegs) :
            csegs[i] = segs[i]
        #end for
        cairo.cairo_set_dash(self._cairobj, ct.byref(csegs), nrsegs, offset)
        return \
            self
    #end set_dash

    @property
    def fill_rule(self) :
        "the current fill rule CAIRO.FILL_RULE_xxx."
        return \
            cairo.cairo_get_fill_rule(self._cairobj)
    #end fill_rule

    @fill_rule.setter
    def fill_rule(self, fill_rule) :
        self.set_fill_rule(fill_rule)
    #end fill_rule

    def set_fill_rule(self, fill_rule) :
        "sets a new fill rule. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the fill_rule property."
        cairo.cairo_set_fill_rule(self._cairobj, fill_rule)
        return \
            self
    #end set_fill_rule

    @property
    def line_cap(self) :
        "the current CAIRO.LINE_CAP_xxx setting."
        return \
            cairo.cairo_get_line_cap(self._cairobj)
    #end line_cap

    @line_cap.setter
    def line_cap(self, line_cap) :
        self.set_line_cap(line_cap)
    #end line_cap

    def set_line_cap(self, line_cap) :
        "sets a new line cap. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the line_cap property."
        cairo.cairo_set_line_cap(self._cairobj, line_cap)
        return \
            self
    #end set_line_cap

    @property
    def line_join(self) :
        "the current CAIRO.LINE_JOIN_xxx setting."
        return \
            cairo.cairo_get_line_join(self._cairobj)
    #end line_join

    @line_join.setter
    def line_join(self, line_join) :
        self.set_line_join(line_join)
    #end line_join

    def set_line_join(self, line_join) :
        "sets a new line join. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the line_join property."
        cairo.cairo_set_line_join(self._cairobj, line_join)
        return \
            self
    #end set_line_join

    @property
    def line_width(self) :
        "the current stroke line width."
        return \
            cairo.cairo_get_line_width(self._cairobj)
    #end line_width

    @line_width.setter
    def line_width(self, width) :
        self.set_line_width(width)
    #end line_width

    def set_line_width(self, width) :
        "sets a new line width. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the line_width property."
        cairo.cairo_set_line_width(self._cairobj, width)
        return \
            self
    #end set_line_width

    @property
    def miter_limit(self) :
        "the current mitre limit."
        return \
            cairo.cairo_get_miter_limit(self._cairobj)
    #end miter_limit

    @miter_limit.setter
    def miter_limit(self, limit) :
        self.set_miter_limit(limit)
    #end miter_limit

    def set_miter_limit(self, limit) :
        "sets a new mitre limit. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the miter_limit property."
        cairo.cairo_set_miter_limit(self._cairobj, limit)
        return \
            self
    #end set_miter_limit

    @property
    def operator(self) :
        "the current drawing operator, as a CAIRO.OPERATOR_xxx code."
        return \
            cairo.cairo_get_operator(self._cairobj)
    #end operator

    @operator.setter
    def operator(self, op) :
        self.set_operator(op)
    #end operator

    def set_operator(self, op) :
        "sets a new drawing operator. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the operator property."
        cairo.cairo_set_operator(self._cairobj, int(op))
        self._check()
        return \
            self
    #end set_operator

    @property
    def tolerance(self) :
        "the curve-flattening tolerance."
        return \
            cairo.cairo_get_tolerance(self._cairobj)
    #end tolerance

    @tolerance.setter
    def tolerance(self, tolerance) :
        self.set_tolerance(self._cairobj, tolerance)
    #end tolerance

    def set_tolerance(self, tolerance) :
        "sets a new curve-rendering tolerance. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the tolerance property."
        cairo.cairo_set_tolerance(self._cairobj, tolerance)
        return \
            self
    #end set_tolerance

    def clip(self) :
        "sets the current clip to the intersection of itself and the" \
        " current path, clearing the latter."
        cairo.cairo_clip(self._cairobj)
        return \
            self
    #end clip

    def clip_preserve(self) :
        "sets the current clip to the intersection of itself and the" \
        " current path, preserving the latter."
        cairo.cairo_clip_preserve(self._cairobj)
        return \
            self
    #end clip_preserve

    @property
    def clip_extents(self) :
        "returns a Rect bounding the current clip."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_clip_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end clip_extents

    def in_clip(self, pt) :
        "is the given Vector pt within the current clip."
        x, y = Vector.from_tuple(pt)
        return \
            cairo.cairo_in_clip(self._cairobj, x, y)
    #end in_clip

    @property
    def clip_rectangle_list(self) :
        "returns a copy of the current clip region as a list of Rects. Whether this works" \
        " depends on the backend."
        rects = cairo.cairo_copy_clip_rectangle_list(self._cairobj)
        try :
            check(rects.contents.status)
            result = list(Rect.from_cairo(rects.contents.rectangles[i]) for i in range(rects.contents.num_rectangles))
        finally :
            cairo.cairo_rectangle_list_destroy(rects)
        #end try
        return \
            result
    #end clip_rectangle_list

    def reset_clip(self) :
        "resets the clip to infinite extent."
        cairo.cairo_reset_clip(self._cairobj)
        return \
            self
    #end reset_clip

    def fill(self) :
        "fills the current path, then clears it."
        cairo.cairo_fill(self._cairobj)
        return \
            self
    #end fill

    def fill_preserve(self) :
        "fills the current path, preserving it."
        cairo.cairo_fill_preserve(self._cairobj)
        return \
            self
    #end fill_preserve

    @property
    def fill_extents(self) :
        "returns a Rect bounding the current path if filled."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_fill_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end fill_extents

    def in_fill(self, pt) :
        "is the given Vector pt within the current path if filled."
        x, y = Vector.from_tuple(pt)
        return \
            cairo.cairo_in_fill(self._cairobj, x, y)
    #end in_fill

    def mask(self, pattern) :
        "fills the current clip area with the current source using the alpha channel" \
        " of the given Pattern as a mask."
        if not isinstance(pattern, Pattern) :
            raise TypeError("pattern is not a Pattern")
        #end if
        cairo.cairo_mask(self._cairobj, pattern._cairobj)
        return \
            self
    #end mask

    def mask_surface(self, surface, origin) :
        "fills the current clip area with the current source using the alpha channel" \
        " of the given Surface, offset to origin, as a mask."
        if not isinstance(surface, Surface) :
            raise TypeError("surface is not a Surface")
        #end if
        x, y = Vector.from_tuple(origin)
        cairo.cairo_mask_surface(self._cairobj, surface._cairobj, x, y)
        return \
            self
    #end mask_surface

    def paint(self) :
        "fills the current clip area with the source."
        cairo.cairo_paint(self._cairobj)
        return \
            self
    #end paint

    def paint_with_alpha(self, alpha) :
        "fills the current clip area with the source faded with the given alpha value."
        cairo.cairo_paint_with_alpha(self._cairobj, alpha)
        return \
            self
    #end paint_with_alpha

    def stroke(self) :
        "strokes the current path, and clears it."
        cairo.cairo_stroke(self._cairobj)
        return \
            self
    #end stroke

    def stroke_preserve(self) :
        "strokes the current path, preserving it."
        cairo.cairo_stroke_preserve(self._cairobj)
        return \
            self
    #end stroke_preserve

    @property
    def stroke_extents(self) :
        "returns a Rect bounding the current path if stroked."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_stroke_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end stroke_extents

    def in_stroke(self, pt) :
        "is the given Vector pt within the current path if stroked."
        x, y = Vector.from_tuple(pt)
        return \
            cairo.cairo_in_stroke(self._cairobj, x, y)
    #end in_stroke

    def copy_page(self) :
        "emits the current page for Surfaces that support multiple pages."
        cairo.cairo_copy_page(self._cairobj)
        self._check()
        return \
            self
    #end copy_page

    def show_page(self) :
        "emits and clears the current page for Surfaces that support multiple pages."
        cairo.cairo_show_page(self._cairobj)
        self._check()
        return \
            self
    #end show_page

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

    # paths <http://cairographics.org/manual/cairo-Paths.html>

    def copy_path(self) :
        "returns a copy of the current path as a Path object."
        temp = cairo.cairo_copy_path(self._cairobj)
        try :
            result = Path.from_cairo(temp)
        finally :
            cairo.cairo_path_destroy(temp)
        #end try
        return \
            result
    #end copy_path

    def copy_path_flat(self) :
        "returns a copy of the current path as a Path object, with curves" \
        " flattened to line segments."
        temp = cairo.cairo_copy_path_flat(self._cairobj)
        try :
            result = Path.from_cairo(temp)
        finally :
            cairo.cairo_path_destroy(temp)
        #end try
        return \
            result
    #end copy_path_flat

    def append_path(self, path, matrix = None) :
        "appends another Path onto the current path, optionally transformed" \
        " by a Matrix."
        # Note I do not use cairo_append_path because my Path structure
        # is implemented entirely in Python.
        if not isinstance(path, Path) :
            raise TypeError("path is not a Path")
        #end if
        path.draw(self, matrix)
        return \
            self
    #end append_path

    @property
    def has_current_point(self) :
        "is current_point currently defined."
        return \
            bool(cairo.cairo_has_current_point(self._cairobj))
    #end has_current_point

    @property
    def current_point(self) :
        "returns the current point if defined, else None."
        if self.has_current_point :
            x = ct.c_double()
            y = ct.c_double()
            cairo.cairo_get_current_point(self._cairobj, ct.byref(x), ct.byref(y))
            result = Vector(x.value, y.value)
        else :
            result = None
        #end if
        return \
            result
    #end current_point

    def new_path(self) :
        "clears the current path."
        cairo.cairo_new_path(self._cairobj)
        return \
            self
    #end new_path

    def new_sub_path(self) :
        "clears the current_point without actually affecting the current path."
        cairo.cairo_new_sub_path(self._cairobj)
        return \
            self
    #end new_sub_path

    def close_path(self) :
        "draws a line from the current point back to the start of the current path segment."
        cairo.cairo_close_path(self._cairobj)
        return \
            self
    #end close_path

    def arc(self, centre, radius, angle1, angle2) :
        "draws a segment of a circular arc in the positive-x-to-positive-y direction." \
        " centre can be a Vector or a tuple of 2 coord values."
        centre = Vector.from_tuple(centre)
        cairo.cairo_arc(self._cairobj, centre.x, centre.y, radius, angle1, angle2)
        return \
            self
    #end arc

    def arc_negative(self, centre, radius, angle1, angle2) :
        "draws a segment of a circular arc in the positive-y-to-positive-x direction." \
        " centre can be a Vector or a tuple of 2 coord values."
        centre = Vector.from_tuple(centre)
        cairo.cairo_arc_negative(self._cairobj, centre.x, centre.y, radius, angle1, angle2)
        return \
            self
    #end arc_negative

    def curve_to(self, p1, p2, p3) :
        "curve_to(p1, p2, p3) or curve_to((x1, y1), (x2, y2), (x3, y3)) -- draws a cubic" \
        " Bézier curve from the current point through the specified control points." \
        " Does a move_to(p1) first if there is no current point."
        p1 = Vector.from_tuple(p1)
        p2 = Vector.from_tuple(p2)
        p3 = Vector.from_tuple(p3)
        cairo.cairo_curve_to(self._cairobj, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
        return \
            self
    #end curve_to

    def line_to(self, p) :
        "line_to(p) or line_to((x, y)) -- draws a line from the current point to the" \
        " new point. Acts like move_to(p) if there is no current point."
        p = Vector.from_tuple(p)
        cairo.cairo_line_to(self._cairobj, p.x, p.y)
        return \
            self
    #end line_to

    def move_to(self, p) :
        "move_to(p) or move_to((x, y)) -- sets the current point to the new point."
        p = Vector.from_tuple(p)
        cairo.cairo_move_to(self._cairobj, p.x, p.y)
        return \
            self
    #end move_to

    def rectangle(self, rect) :
        "appends a rectangular outline to the current path."
        cairo.cairo_rectangle(self._cairobj, rect.left, rect.top, rect.width, rect.height)
        return \
            self
    #end rectangle

    def glyph_path(self, glyphs) :
        "glyphs is a sequence of Glyph objects; appends the glyph outlines to" \
        " the current path."
        buf, nr_glyphs = glyphs_to_cairo(glyphs)
        cairo.cairo_glyph_path(self._cairobj, ct.byref(buf), nr_glyphs)
        return \
            self
    #end glyph_path

    def text_path(self, text) :
        "adds text outlines to the current path."
        cairo.cairo_text_path(self._cairobj, text.encode("utf-8"))
        return \
            self
    #end text_path

    def rel_curve_to(self, p1, p2, p3) :
        "rel_curve_to(p1, p2, p3) or rel_curve_to((x1, y1), (x2, y2), (x3, y3)) -- does" \
        " a curve_to through the specified control points interpreted as offsets from" \
        " the current point. There must be a current point."
        p1 = Vector.from_tuple(p1)
        p2 = Vector.from_tuple(p2)
        p3 = Vector.from_tuple(p3)
        cairo.cairo_rel_curve_to(self._cairobj, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
        return \
            self
    #end rel_curve_to

    def rel_line_to(self, p) :
        "rel_line_to(p) or rel_line_to((x, y)) -- does a line_to to the specified point" \
        " interpreted as an offset from the current point. There must be a current point."
        p = Vector.from_tuple(p)
        cairo.cairo_rel_line_to(self._cairobj, p.x, p.y)
        return \
            self
    #end rel_line_to

    def rel_move_to(self, p) :
        "rel_move_to(p) or rel_move_to((x, y)) -- offsets the current point by the" \
        " specified Vector amount. There must be a current point."
        p = Vector.from_tuple(p)
        cairo.cairo_rel_move_to(self._cairobj, p.x, p.y)
        return \
            self
    #end rel_move_to

    @property
    def path_extents(self) :
        "returns a Rect bounding the current path."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_path_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end path_extents

    # Transformations <http://cairographics.org/manual/cairo-Transformations.html>

    def translate(self, v) :
        "translate(Vector) or translate((x, y))\n" \
        "applies a translation to the current coordinate system."
        tx, ty = Vector.from_tuple(v)
        cairo.cairo_translate(self._cairobj, tx, ty)
        return \
            self
    #end translate

    def scale(self, s) :
        "scale(Vector) or scale((x, y))\n" \
        "applies a scaling to the current coordinate system."
        sx, sy = Vector.from_tuple(s)
        cairo.cairo_scale(self._cairobj, sx, sy)
        return \
            self
    #end scale

    def rotate(self, angle) :
        "applies a rotation by the specified angle to the current coordinate system."
        cairo.cairo_rotate(self._cairobj, angle)
        return \
            self
    #end rotate

    def transform(self, m) :
        "appends Matrix m onto the current coordinate transformation."
        m = m.to_cairo()
        cairo.cairo_transform(self._cairobj, ct.byref(m))
        return \
            self
    #end transform

    @property
    def matrix(self) :
        "the current transformation Matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_get_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end matrix

    @matrix.setter
    def matrix(self, m) :
        self.set_matrix(m)
    #end matrix

    def set_matrix(self, m) :
        "sets a new transformation matrix. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the matrix property."
        m = m.to_cairo()
        cairo.cairo_set_matrix(self._cairobj, ct.byref(m))
        self._check()
        return \
            self
    #end set_matrix

    def identity_matrix(self) :
        "resets the coordinate transformation to the identity Matrix."
        cairo.cairo_identity_matrix(self._cairobj)
        return \
            self
    #end identity_matrix

    def user_to_device(self, p) :
        "returns the transformed Vector in device coordinates corresponding to Vector" \
        " p in user coordinates."
        x = ct.c_double()
        y = ct.c_double()
        x.value, y.value = Vector.from_tuple(p)
        cairo.cairo_user_to_device(self._cairobj, ct.byref(x), ct.byref(y))
        return \
            Vector(x.value, y.value)
    #end user_to_device

    def user_to_device_distance(self, p) :
        "returns the transformed Vector in device coordinates corresponding to Vector" \
        " p in user coordinates, ignoring any translation."
        x = ct.c_double()
        y = ct.c_double()
        x.value, y.value = Vector.from_tuple(p)
        cairo.cairo_user_to_device_distance(self._cairobj, ct.byref(x), ct.byref(y))
        return \
            Vector(x.value, y.value)
    #end user_to_device_distance

    def device_to_user(self, p) :
        "returns the transformed Vector in user coordinates corresponding to Vector" \
        " p in device coordinates."
        x = ct.c_double()
        y = ct.c_double()
        x.value, y.value = Vector.from_tuple(p)
        cairo.cairo_device_to_user(self._cairobj, ct.byref(x), ct.byref(y))
        return \
            Vector(x.value, y.value)
    #end device_to_user

    def device_to_user_distance(self, p) :
        "returns the transformed Vector in user coordinates corresponding to Vector" \
        " p in device coordinates, ignoring any translation."
        x = ct.c_double()
        y = ct.c_double()
        x.value, y.value = Vector.from_tuple(p)
        cairo.cairo_device_to_user_distance(self._cairobj, ct.byref(x), ct.byref(y))
        return \
            Vector(x.value, y.value)
    #end device_to_user_distance

    # Text <http://cairographics.org/manual/cairo-text.html>
    # (except toy_font_face stuff, which goes in FontFace)

    def select_font_face(self, family, slant, weight) :
        "toy selection of a font face."
        cairo.cairo_select_font_face(self._cairobj, family.encode("utf-8"), slant, weight)
        return \
            self
    #end select_font_face

    def set_font_size(self, size) :
        "sets the font matrix to a scaling by the specified size."
        cairo.cairo_set_font_size(self._cairobj, size)
        return \
            self
    #end set_font_size

    @property
    def font_matrix(self) :
        "the current font matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_get_font_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end font_matrix

    @font_matrix.setter
    def font_matrix(self, matrix) :
        self.set_font_matrix(matrix)
    #end font_matrix

    def set_font_matrix(self, matrix) :
        "sets a new font matrix. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the font_matrix property."
        if not isinstance(matrix, Matrix) :
            raise TypeError("matrix must be a Matrix")
        #end if
        matrix = matrix.from_cairo()
        cairo.cairo_set_font_matrix(self._cairobj, ct.byref(matrix))
        return \
            self
    #end set_font_matrix

    @property
    def font_options(self) :
        "a copy of the current font options."
        result = FontOptions()
        cairo.cairo_get_font_options(self._cairobj, result._cairobj)
        return \
            result
    #end font_options

    @font_options.setter
    def font_options(self, options) :
        self.set_font_options(options)
    #end font_options

    def set_font_options(self, options) :
        "sets new font options. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the font_options property."
        if not isinstance(options, FontOptions) :
            raise TypeError("options must be a FontOptions")
        #end if
        cairo.cairo_set_font_options(self._cairobj, options._cairobj)
        return \
            self
    #end set_font_options

    @property
    def font_face(self) :
        "the current font face."
        return \
            FontFace(cairo.cairo_get_font_face(self._cairobj))
    #end font_face

    @font_face.setter
    def font_face(self, font_face) :
        self.set_font_face(font_face)
    #end font_face

    def set_font_face(self, font_face) :
        "sets a new font face. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the font_face property."
        if not isinstance(font_face, FontFace) :
            raise TypeError("font_face must be a FontFace")
        #end if
        cairo.cairo_set_font_face(self._cairobj, font_face._cairobj)
        return \
            self
    #end set_font_face

    @property
    def scaled_font(self) :
        "the current scaled font."
        return \
            ScaledFont(cairo.cairo_get_scaled_font(self._cairobj))
    #end scaled_font

    @scaled_font.setter
    def scaled_font(self, scaled_font) :
        self.set_scaled_font(scaled_font)
    #end scaled_font

    def set_scaled_font(self, scaled_font) :
        "sets a new scaled font face. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the scaled_font property."
        if not isinstance(scaled_font, ScaledFont) :
            raise TypeError("scaled_font must be a ScaledFont")
        #end if
        cairo.cairo_set_scaled_font(self._cairobj, scaled_font._cairobj)
        return \
            self
    #end set_scaled_font

    def show_text(self, text) :
        "renders the specified text starting at the current point."
        cairo.cairo_show_text(self._cairobj, text.encode("utf-8"))
        return \
            self
    #end show_text

    def show_glyphs(self, glyphs) :
        "glyphs must be a sequence of Glyph objects, to be rendered starting" \
        " at the current point."
        buf, nr_glyphs = glyphs_to_cairo(glyphs)
        cairo.cairo_show_glyphs(self._cairobj, ct.byref(buf), nr_glyphs)
        return \
            self
    #end show_glyphs

    # TODO: show_text_glyphs

    @property
    def font_extents(self) :
        "returns a FontExtents object giving information about the current font settings."
        result = CAIRO.font_extents_t()
        cairo.cairo_font_extents(self._cairobj, ct.byref(result))
        return \
            FontExtents.from_cairo(result)
    #end font_extents

    def text_extents(self, text) :
        "returns a TextExtents object giving information about drawing the" \
        " specified text at the current font settings."
        result = CAIRO.text_extents_t()
        cairo.cairo_text_extents(self._cairobj, text.encode("utf-8"), ct.byref(result))
        return \
            TextExtents.from_cairo(result)
    #end text_extents

    def glyph_extents(self, glyphs) :
        "returns a TextExtents object giving information about drawing the" \
        " specified sequence of Glyphs at the current font settings."
        buf, nr_glyphs = glyphs_to_cairo(glyphs)
        result = CAIRO.text_extents_t()
        cairo.cairo_glyph_extents(self._cairobj, buf, nr_glyphs, ct.byref(result))
        return \
            TextExtents.from_cairo(result)
    #end glyph_extents

#end Context

def file_write_func(fileobj) :
    "fileobj must have a .write method that accepts a single bytes argument." \
    " This function returns a write_func that can be passed to the various" \
    " create_for_xxx_stream and write_to_xxx_stream methods which will write" \
    " the data to the file object. The write_func ignores its closure argument," \
    " so feel free to pass None for that."

    def write_data(_, data, length) :
        buf = array.array("B", (0,) * length)
        libc.memcpy(buf.buffer_info()[0], data, length)
        fileobj.write(buf.tobytes())
        return \
            CAIRO.STATUS_SUCCESS
    #end write_data

#begin file_write_func
    return \
        write_data
#end file_write_func

class Surface :
    "base class for Cairo surfaces. Do not instantiate directly; use create methods" \
    " provided by subclasses."
    # <http://cairographics.org/manual/cairo-cairo-surface-t.html>

    __slots__ = ("_cairobj", "_user_data") # to forestall typos

    def _check(self) :
        # check for error from last operation on this Surface.
        check(cairo.cairo_surface_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
        self._user_data = {}
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_surface_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def __eq__(self, other) :
        "do the two Surface objects refer to the same surface. Needed because" \
        " methods like Context.target and Pattern.surface cannot return the same" \
        " Surface object each time."
        return \
            isinstance(other, Surface) and self._cairobj == other._cairobj
    #end __eq__

    @property
    def type(self) :
        "returns the surface type code CAIRO.SURFACE_TYPE_xxx."
        return \
            cairo.cairo_surface_get_type(self._cairobj)
    #end type

    def create_similar(self, content, dimensions) :
        "creates a new Surface with the specified Vector dimensions, which is as" \
        " compatible as possible with this one. content is a CAIRO.CONTENT_xxx value."
        dimensions = round(Vector.from_tuple(dimensions))
        return \
            Surface(cairo.cairo_surface_create_similar(self._cairobj, content, dimensions.x, dimensions.y))
            # fixme: need to choose right Surface subclass based on result surface type
    #end create_similar

    def create_similar_image(self, format, dimensions) :
        "creates an ImageSurface with the specified CAIRO.FORMAT_xxx format and Vector" \
        " dimensions that is as compatible as possible with this one."
        dimensions = round(Vector.from_tuple(dimensions))
        return \
            ImageSurface(cairo.cairo_surface_create_similar_image(self._cairobj, format, dimensions.x, dimensions.y))
    #end create_similar_image

    def create_for_rectangle(self, bounds) :
        "creates a new Surface where drawing is strictly limited to the bounds Rect" \
        " within this one."
        return \
            type(self)(cairo.cairo_surface_create_for_rectangle(self._cairobj, bounds.left, bounds.top, bounds.width, bounds.height))
            # assumes it returns same type of surface as self!
    #end create_for_rectangle

    def flush(self) :
        "ensures that Cairo has finished all drawing to this Surface, restoring" \
        " any temporary modifications made to its state."
        cairo.cairo_surface_flush(self._cairobj)
        return \
            self
    #end flush

    @property
    def device(self) :
        "returns the Device for this Surface."
        result = cairo.cairo_surface_get_device(self._cairobj)
        if result != None :
            result = Device(result)
        #end if
        return \
            result
    #end device

    @property
    def font_options(self) :
        "returns a copy of the font_options for this Surface."
        result = FontOptions()
        cairo.cairo_surface_get_font_options(self._cairobj, result._cairobj)
        return \
            result
    #end font_options

    @property
    def content(self) :
        "returns the content code CAIRO.CONTENT_xxx for this Surface."
        return \
            cairo.cairo_surface_get_content(self._cairobj)
    #end content

    # TODO: mark_dirty, device_offset, fallback_resolution

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

    # TODO: has_show_text_glyphs, mime_data, map/unmap image
    # <http://cairographics.org/manual/cairo-cairo-surface-t.html>

    def copy_page(self) :
        "emits the current page for Surfaces that support multiple pages."
        cairo.cairo_surface_copy_page(self._cairobj)
        self._check()
        return \
            self
    #end copy_page

    def show_page(self) :
        "emits and clears the current page for Surfaces that support multiple pages."
        cairo.cairo_surface_show_page(self._cairobj)
        self._check()
        return \
            self
    #end show_page

    def write_to_png(self, filename) :
        check(cairo.cairo_surface_write_to_png(self._cairobj, filename.encode("utf-8")))
        return \
            self
    #end write_to_png

    def write_to_png_stream(self, write_func, closure) :
        "direct low-level interface to cairo_image_surface_write_to_png_stream." \
        " write_func must match signature of CAIRO.write_func_t, while closure is a" \
        " ctypes.c_void_p."
        c_write_func = CAIRO.write_func_t(write_func)
        check(cairo.cairo_surface_write_to_png_stream(self._cairobj, c_write_func, closure))
        return \
            self
    #end write_to_png_stream

    def to_png_bytes(self) :
        "converts the contents of the Surface to a sequence of PNG bytes which" \
        " is returned."

        offset = 0

        def write_data(_, data, length) :
            nonlocal offset
            result.extend(length * (0,))
            libc.memcpy(result.buffer_info()[0] + offset, data, length)
            offset += length
            return \
                CAIRO.STATUS_SUCCESS
        #end write_data

    #begin to_png_bytes
        result = array.array("B")
        self.write_to_png_stream(write_data, None)
        return \
            result.tobytes()
    #end to_png_bytes

#end Surface

class ImageSurface(Surface) :
    "A Cairo image surface. Do not instantiate directly; instead," \
    " call one of the create methods."

    __slots__ = ("_arr",) # to forestall typos

    @staticmethod
    def create(format, dimensions) :
        "creates a new ImageSurface with dynamically-allocated memory for the pixels." \
        " dimensions can be a Vector or a (width, height) tuple."
        dimensions = Vector.from_tuple(dimensions)
        return \
            ImageSurface(cairo.cairo_image_surface_create(int(format), int(dimensions.x), int(dimensions.y)))
    #end create

    @staticmethod
    def create_from_png(filename) :
        "loads an image from a PNG file and creates an ImageSurface for it."
        return \
            ImageSurface(cairo.cairo_image_surface_create_from_png(filename.encode("utf-8")))
    #end create_from_png

    @staticmethod
    def create_from_png_stream(read_func, closure) :
        "direct low-level interface to cairo_image_surface_create_from_png_stream." \
        " read_func must match signature CAIRO.read_func_t, while closure is a ctypes.c_void_p."
        c_read_func = CAIRO.read_func_t(read_func)
        return \
            ImageSurface(cairo.cairo_image_surface_create_from_png_stream(c_read_func, closure))
    #end create_from_png_stream

    @staticmethod
    def create_from_png_bytes(data) :
        "creates an ImageSurface from a PNG format data sequence. This can be" \
        " of the bytes or bytearray types, or an array.array with \"B\" type code."

        offset = 0

        def read_data(_, data, length) :
            nonlocal offset
            if offset + length <= len(data) :
                libc.memcpy(data, baseadr + offset, length)
                offset += length
                status = CAIRO.STATUS_SUCCESS
            else :
                status = CAIRO.STATUS_READ_ERROR
            #end if
            return \
                status
        #end read_data

    #begin create_from_png_bytes
        if isinstance(data, bytes) or isinstance(data, bytearray) :
            data = array.array("B", data)
        elif not isinstance(data, array.array) or data.typecode != "B" :
            raise TypeError("data is not bytes, bytearray or array of bytes")
        #end if
        baseadr = data.buffer_info()[0]
        return \
            ImageSurface.create_from_png_stream(read_data, None)
    #end create_from_png_bytes

    @staticmethod
    def format_stride_for_width(format, width) :
        "returns a suitable stride value (number of bytes per row of pixels) for" \
        " an ImageSurface with the specified format CAIRO.FORMAT_xxx and pixel width."
        return \
            cairo.cairo_format_stride_for_width(int(format), int(width))
    #end format_stride_for_width

    # TODO: get_data?

    @property
    def format(self) :
        "the pixel format CAIRO.FORMAT_xxx."
        result = cairo.cairo_image_surface_get_format(self._cairobj)
        self._check()
        return \
            result
    #end format

    @property
    def width(self) :
        "the width in pixels."
        result = cairo.cairo_image_surface_get_width(self._cairobj)
        self._check()
        return \
            result
    #end width

    @property
    def height(self) :
        "the height in pixels."
        result = cairo.cairo_image_surface_get_height(self._cairobj)
        self._check()
        return \
            result
    #end height

    @property
    def dimensions(self) :
        "the dimensions in pixels, as a Vector."
        return \
            Vector(self.width, self.height)
    #end dimensions

    @property
    def stride(self) :
        "the number of bytes per row of pixels."
        result = cairo.cairo_image_surface_get_stride(self._cairobj)
        self._check()
        return \
            result
    #end stride

    @staticmethod
    def create_for_array(arr, format, dimensions, stride) :
        "calls cairo_image_surface_create_for_data on arr, which must be" \
        " a Python array.array object."
        width, height = Vector.from_tuple(dimensions)
        address, length = arr.buffer_info()
        assert height * stride <= length * arr.itemsize
        result = ImageSurface(cairo.cairo_image_surface_create_for_data(ct.c_void_p(address), format, width, height, stride))
        result._arr = arr # to ensure it doesn't go away prematurely
        return \
            result
    #end create_for_array

    # do I need a more general interface to create_for_data than create_for_array?

#end ImageSurface

class PDFSurface(Surface) :
    "A Cairo surface that outputs its renderings to a PDF file. Do not instantiate" \
    " directly; use one of the create methods."

    __slots__ = () # to forestall typos

    @staticmethod
    def create(filename, dimensions_in_points) :
        "creates a PDF surface that outputs to the specified file, with the dimensions" \
        " of each page given by the Vector dimensions_in_points."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        return \
            PDFSurface(cairo.cairo_pdf_surface_create(filename.encode("utf-8"), dimensions_in_points.x, dimensions_in_points.y))
    #end create

    @staticmethod
    def create_for_stream(write_func, closure, dimensions_in_points) :
        "direct low-level interface to cairo_pdf_surface_create_for_stream." \
        " write_func must match signature of CAIRO.write_func_t, while closure is a" \
        " ctypes.c_void_p."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        c_write_func = CAIRO.write_func_t(write_func)
        return \
            PDFSurface(cairo.cairo_pdf_surface_create_for_stream(c_write_func, closure, dimensions_in_points.x, dimensions_in_points.y))
    #end create_for_stream

    def restrict_to_version(self, version) :
        "restricts the version of PDF file created. If used, should" \
        " be called before any actual drawing is done."
        cairo.cairo_pdf_surface_restrict_to_version(self._cairobj, version)
        self._check()
        return \
            self
    #end restrict_to_version

    @staticmethod
    def get_versions() :
        "returns a tuple of supported PDF version number codes CAIRO.PDF_VERSION_xxx."
        versions = ct.POINTER(ct.c_int)()
        num_versions = ct.c_int()
        cairo.cairo_pdf_get_versions(ct.byref(versions), ct.byref(num_versions))
        return \
            tuple(versions[i] for i in range(num_versions.value))
    #end get_versions

    @staticmethod
    def version_to_string(version) :
        "returns the canonical version string for the specified PDF" \
        " version code CAIRO.PDF_VERSION_xxx."
        result = cairo.cairo_pdf_version_to_string(version)
        if bool(result) :
            result = result.decode("utf-8")
        else :
            result = None
        #end if
        return \
            result
    #end version_to_string

    def set_size(self, dimensions_in_points) :
        "resizes the page. Must be empty at this point (e.g. immediately" \
        " after show_page or initial creation)."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        cairo.cairo_pdf_surface_set_size(self._cairobj, dimensions_in_points.x, dimensions_in_points.y)
        self._check()
        return \
            self
    #end set_size

#end PDFSurface

class PSSurface(Surface) :
    "a Cairo surface which translates drawing actions into PostScript program sequences." \
    " Do not instantiate directly; use one of the create methods."

    __slots__ = () # to forestall typos

    @staticmethod
    def create(filename, dimensions_in_points) :
        "creates a PostScript surface that outputs to the specified file, with the dimensions" \
        " of each page given by the Vector dimensions_in_points."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        return \
            PSSurface(cairo.cairo_ps_surface_create(filename.encode("utf-8"), dimensions_in_points.x, dimensions_in_points.y))
    #end create

    @staticmethod
    def create_for_stream(write_func, closure, dimensions_in_points) :
        "direct low-level interface to cairo_ps_surface_create_for_stream." \
        " write_func must match signature of CAIRO.write_func_t, while closure is a" \
        " ctypes.c_void_p."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        c_write_func = CAIRO.write_func_t(write_func)
        return \
            PSSurface(cairo.cairo_ps_surface_create_for_stream(c_write_func, closure, dimensions_in_points.x, dimensions_in_points.y))
    #end create_for_stream

    def restrict_to_level(self, level) :
        "restricts the language level of PostScript created, one of the CAIRO.PS_LEVEL_xxx" \
        " codes. If used, should be called before any actual drawing is done."
        cairo.cairo_ps_surface_restrict_to_level(self._cairobj, level)
        self._check()
        return \
            self
    #end restrict_to_level

    @staticmethod
    def get_levels() :
        "returns a tuple of supported PostScript language level codes CAIRO.PS_LEVEL_xxx."
        levels = ct.POINTER(ct.c_int)()
        num_levels = ct.c_int()
        cairo.cairo_ps_get_levels(ct.byref(levels), ct.byref(num_levels))
        return \
            tuple(levels[i] for i in range(num_levels.value))
    #end get_levels

    @staticmethod
    def level_to_string(level) :
        "returns the canonical string for the specified PostScript" \
        " language level code CAIRO.PS_LEVEL_xxx."
        result = cairo.cairo_ps_level_to_string(level)
        if bool(result) :
            result = result.decode("utf-8")
        else :
            result = None
        #end if
        return \
            result
    #end level_to_string

    @property
    def eps(self) :
        "whether the Surface outputs Encapsulated PostScript."
        result = cairo.cairo_ps_surface_get_eps(self._cairobj)
        self._check()
        return \
            result
    #end eps

    @eps.setter
    def eps(self, eps) :
        self.set_eps(eps)
    #end eps

    def set_eps(self, eps) :
        "specifies whether the Surface outputs Encapsulated PostScript."
        cairo.cairo_ps_surface_set_eps(self._cairobj, eps)
        self._check()
        return \
            self
    #end set_eps

    def set_size(self, dimensions_in_points) :
        "resizes the page. Must be empty at this point (e.g. immediately" \
        " after show_page or initial creation)."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        cairo.cairo_ps_surface_set_size(self._cairobj, dimensions_in_points.x, dimensions_in_points.y)
        self._check()
        return \
            self
    #end set_size

    def dsc_begin_setup(self) :
        "indicates that subsequent calls to dsc_comment should go to the Setup section."
        cairo.cairo_ps_surface_dsc_begin_setup(self._cairobj)
        self._check()
        return \
            self
    #end dsc_begin_setup

    def dsc_begin_page_setup(self) :
        "indicates that subsequent calls to dsc_comment should go to the PageSetup section."
        cairo.cairo_ps_surface_dsc_begin_page_setup(self._cairobj)
        self._check()
        return \
            self
    #end dsc_begin_page_setup

    def dsc_comment(self, comment) :
        "emits a DSC comment."
        cairo.cairo_ps_surface_dsc_comment(self._cairobj, comment.encode("utf-8"))
        self._check()
        return \
            self
    #end dsc_comment

#end PSSurface

class RecordingSurface(Surface) :
    "a Surface that records the sequence of drawing calls made into it" \
    " and plays them back when used as a source Pattern. Do not instantiate" \
    " directly; use the create method."

    __slots__ = () # to forestall typos

    @staticmethod
    def create(content, extents = None) :
        "content is a CAIRO.CONTENT_xxx value, and extents is an optional" \
        " Rect defining the drawing extents. If omitted, the extents are unbounded."
        if extents != None :
            extents = extents.to_cairo()
            extentsarg = ct.byref(extents)
        else :
            extentsarg = None
        #end if
        return \
            RecordingSurface(cairo.cairo_recording_surface_create(content, extentsarg))
    #end create

    @property
    def ink_extents(self) :
        "the extents of the operations recorded, as a Rect."
        x0 = ct.c_double()
        y0 = ct.c_double()
        width = ct.c_double()
        height = ct.c_double()
        cairo.cairo_recording_surface_ink_extents(self._cairobj, ct.byref(x0), ct.byref(y0), ct.byref(width), ct.byref(height))
        return \
            Rect(x0.value, y0.value, width.value, height.value)
    #end ink_extents

    @property
    def extents(self) :
        "the original extents the surface was created with as a Rect, or None if unbounded."
        result = CAIRO.rectangle_t()
        if cairo.cairo_recording_surface_get_extents(self._cairobj, ct.byref(result)) :
            result = Rect.from_cairo(result)
        else :
            result = None
        #end if
        return \
            result
    #end extents

#end RecordingSurface

class SVGSurface(Surface) :
    "Surface that writes its contents to an SVG file. Do not instantiate directly;" \
    " use one of the create methods."

    __slots__ = () # to forestall typos

    @staticmethod
    def create(filename, dimensions_in_points) :
        "creates an SVG surface that outputs to the specified file, with the dimensions" \
        " of each page given by the Vector dimensions_in_points."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        return \
            SVGSurface(cairo.cairo_svg_surface_create(filename.encode("utf-8"), dimensions_in_points.x, dimensions_in_points.y))
    #end create

    @staticmethod
    def create_for_stream(write_func, closure, dimensions_in_points) :
        "direct low-level interface to cairo_svg_surface_create_for_stream." \
        " write_func must match signature of CAIRO.write_func_t, while closure is a" \
        " ctypes.c_void_p."
        dimensions_in_points = Vector.from_tuple(dimensions_in_points)
        c_write_func = CAIRO.write_func_t(write_func)
        return \
            SVGSurface(cairo.cairo_svg_surface_create_for_stream(c_write_func, closure, dimensions_in_points.x, dimensions_in_points.y))
    #end create_for_stream

    def restrict_to_version(self, version) :
        "restricts the version of SVG file created. If used, must" \
        " be called before any actual drawing is done."
        cairo.cairo_svg_surface_restrict_to_version(self._cairobj, version)
        self._check()
        return \
            self
    #end restrict_to_version

    @staticmethod
    def get_versions() :
        "returns a tuple of supported SVG version number codes CAIRO.SVG_VERSION_xxx."
        versions = ct.POINTER(ct.c_int)()
        num_versions = ct.c_int()
        cairo.cairo_svg_get_versions(ct.byref(versions), ct.byref(num_versions))
        return \
            tuple(versions[i] for i in range(num_versions.value))
    #end get_versions

    @staticmethod
    def version_to_string(version) :
        "returns the canonical version string for the specified SVG" \
        " version code CAIRO.SVG_VERSION_xxx."
        result = cairo.cairo_svg_version_to_string(version)
        if bool(result) :
            result = result.decode("utf-8")
        else :
            result = None
        #end if
        return \
            result
    #end version_to_string

#end SVGSurface

class Device :
    "a Cairo device_t object. Do not instantiate directly; get from Surface.device" \
    " or ScriptDevice.create."
    # <http://cairographics.org/manual/cairo-cairo-device-t.html>

    __slots__ = ("_cairobj", "_user_data") # to forestall typos

    def _check(self) :
        # check for error from last operation on this Surface.
        check(cairo.cairo_device_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
        self._user_data = {}
    #end __init__

    @property
    def type(self) :
        "the type of the Device, a CAIRO.DEVICE_TYPE_xxx code."
        return \
            cairo.cairo_device_get_type(self._cairobj)
    #end type

    # TODO: acquire, release, observer stuff

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

#end Device

class ScriptDevice(Device) :
    "for rendering to replayable Cairo scripts."
    # <http://cairographics.org/manual/cairo-Script-Surfaces.html>

    __slots__ = () # to forestall typos

    @staticmethod
    def create(filename) :
        "creates a ScriptDevice that outputs to the specified file."
        return \
            ScriptDevice(cairo.cairo_script_create(filename.encode("utf-8")))
    #end create

    @staticmethod
    def create_for_stream(write_func, closure) :
        "direct low-level interface to cairo_script_create_for_stream." \
        " write_func must match signature of CAIRO.write_func_t, while closure is a" \
        " ctypes.c_void_p."
        c_write_func = CAIRO.write_func_t(write_func)
        return \
            ScriptDevice(cairo.cairo_script_create_for_stream(c_write_func, closure))
    #end create_for_stream

    def from_recording_surface(self, recording_surface) :
        "converts the recorded operations in recording_surface (a RecordingSurface)" \
        " into a script."
        if not isinstance(recording_surface, RecordingSurface) :
            raise TypeError("recording_surface must be a RecordingSurface")
        #end if
        check(cairo.cairo_script_from_recording_surface(self._cairobj, recording_surface._cairobj))
    #end create_from_recording_surface

    @property
    def mode(self) :
        "the current mode CAIRO.SCRIPT_MODE_xxx value."
        return \
            cairo.cairo_script_get_mode(self._cairobj)
    #end mode

    @mode.setter
    def mode(self, mode) :
        cairo.cairo_script_set_mode(self._cairobj, mode)
        self._check()
    #end mode

    def surface_create(self, content, dimensions) :
        "creates a new Surface that will emit its rendering through this ScriptDevice."
        dimensions = Vector.from_tuple(dimensions)
        return \
            Surface(cairo.cairo_script_surface_create(self._cairobj, content, dimensions.x, dimensions.y))
    #end surface_create

    def surface_create_for_target(self, target) :
        "creates a proxy Surface that will render to Surface target and record its" \
        " operations through this ScriptDevice."
        if not isinstance(target, Surface) :
            raise TypeError("target must be a Surface")
        #end if
        return \
            Surface(cairo.cairo_script_surface_create_for_target(self._cairobj, target._cairobj))
    #end surface_create_for_target

    def write_comment(self, comment) :
        "writes a comment to the script. comment can be a string or bytes."
        if isinstance(comment, str) :
            comment = comment.encode("utf-8")
        elif not isinstance(comment, bytes) :
            raise TypeError("comment must be str or bytes")
        #end if
        c_comment = (ct.c_ubyte * len(comment))()
        for i in range(len(comment)) :
            c_comment[i] = comment[i]
        #end for
        cairo.cairo_script_write_comment(self._cairobj, ct.byref(c_comment), len(comment))
    #end write_comment

#end ScriptDevice

class Colour :
    "a representation of a colour plus alpha, convertible to/from the various colour" \
    " spaces available in the Python colorsys module. Internal representation is" \
    " always (r, g, b, a)."

    __slots__ = ("r", "g", "b", "a") # to forestall typos

    def __init__(self, r, g, b, a) :
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    #end __init__

    def __getitem__(self, i) :
        "being able to access elements by index allows a Colour to be cast to a tuple or list."
        return \
            (self.r, self.g, self.b, self.a)[i]
    #end __getitem__

    def __repr__(self) :
        return \
            "Colour%s" % repr(tuple(self))
    #end __repr__

    @classmethod
    def _alpha_tuple(celf, c) :
        # ensures that c is a tuple of 4 elements, appending a default alpha if omitted
        c = tuple(c)
        if len(c) == 3 :
            c = c + (1,) # default to full-opaque alpha
        elif len(c) != 4 :
            raise TypeError("colour tuple must have 3 or 4 elements")
        #end if
        return \
            c
    #end _alpha_tuple

    @classmethod
    def _convert_space(celf, c, conv) :
        # puts the non-alpha components of c through the conversion function conv
        # and returns the result with the alpha restored.
        c = celf._alpha_tuple(c)
        return \
            conv(*c[:3]) + (c[3],)
    #end _convert_space

    @staticmethod
    def from_rgba(c) :
        "constructs a Colour from an (r, g, b) or (r, g, b, a) tuple."
        return \
            Colour(*Colour._alpha_tuple(c))
    #end from_rgba

    @staticmethod
    def from_hsva(c) :
        "constructs a Colour from an (h, s, v) or (h, s, v, a) tuple."
        return \
            Colour(*Colour._convert_space(c, colorsys.hsv_to_rgb))
    #end from_hsva

    @staticmethod
    def from_hlsa(c) :
        "constructs a Colour from an (h, l, s) or (h, l, s, a) tuple."
        return \
            Colour(*Colour._convert_space(c, colorsys.hls_to_rgb))
    #end from_hlsa

    @staticmethod
    def from_yiqa(c) :
        "constructs a Colour from a (y, i, q) or (y, i, q, a) tuple."
        return \
            Colour(*Colour._convert_space(c, colorsys.yiq_to_rgb))
    #end from_yiqa

    @staticmethod
    def grey(i, a = 1) :
        "constructs a monochrome Colour with r, g and b components set to i" \
        " and alpha set to a."
        return \
            Colour(i, i, i, a)
    #end grey

    def to_rgba(self) :
        "returns an (r, g, b, a) tuple. Present just for completeness," \
        " since the Colour object itself can be directly converted to" \
        " such a tuple."
        return \
            tuple(self)
    #end to_rgba

    def to_hsva(self) :
        "returns an (h, s, v, a) tuple."
        return \
            Colour._convert_space(self, colorsys.rgb_to_hsv)
    #end to_hsva

    def to_hlsa(self) :
        "returns an (h, l, s, a) tuple."
        return \
            Colour._convert_space(self, colorsys.rgb_to_hls)
    #end to_hlsa

    def to_yiqa(self) :
        "returns a (y, i, q, a) tuple."
        return \
            Colour._convert_space(self, colorsys.rgb_to_yiq)
    #end to_yiqa

    def replace_alpha(self, new_alpha) :
        "returns a new Colour with the same r, g and b components but the specified alpha."
        return \
            Colour(self.r, self.g, self.b, new_alpha)
    #end replace_alpha

    def combine(self, other, rgb_func, alpha_func) :
        "produces a combination of this Colour with other by applying the specified" \
        " functions on the respective components. rgb_func must take four arguments" \
        " (ac, aa, bc, ba), where ac and bc are the corresponding colour components" \
        " (r, g or b) and aa and ba are the alphas, and returns a new value for that" \
        " colour component. alpha_func takes two arguments (aa, ba), being the alpha" \
        " values, and returns the new alpha."
        return \
            Colour \
              (
                r = rgb_func(self.r, self.a, other.r, other.a),
                g = rgb_func(self.g, self.a, other.g, other.a),
                b = rgb_func(self.b, self.a, other.b, other.a),
                a = alpha_func(self.a, other.a)
              )
    #end combine

    def mix(self, other, amt) :
        "returns a mixture of this Colour with other in the proportion given by amt;" \
        " if amt is 0, then the result is purely this colour, while if amt is 1, then" \
        " it is purely other."
        return \
            self.combine \
              (
                other = other,
                rgb_func = lambda ac, aa, bc, ba : interp(amt, ac, bc),
                alpha_func = lambda aa, ba : interp(amt, aa, ba)
              )
    #end mix

#end Colour

class Pattern :
    "a Cairo Pattern object. Do not instantiate directly; use one of the create methods."
    # <http://cairographics.org/manual/cairo-cairo-pattern-t.html>

    __slots__ = ("_cairobj", "_user_data", "_surface") # to forestall typos

    def _check(self) :
        # check for error from last operation on this Pattern.
        check(cairo.cairo_pattern_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
        self._user_data = {}
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_pattern_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def __eq__(self, other) :
        "do the two Pattern objects refer to the same Pattern. Needed because" \
        " Context.source cannot return the same Pattern object each time."
        return \
            isinstance(other, Pattern) and self._cairobj == other._cairobj
    #end __eq__

    def add_colour_stop(self, offset, c) :
        "adds a colour stop. This must be a gradient Pattern, offset is a number in [0, 1]" \
        " and c must be a Colour or tuple. Returns the same Pattern, to allow for" \
        " method chaining."
        cairo.cairo_pattern_add_color_stop_rgba(*((self._cairobj, offset) + tuple(Colour.from_rgba(c))))
        self._check()
        return \
            self
    #end add_colour_stop

    def add_colour_stops(self, stops) :
        "adds a whole lot of colour stops at once. stops must be a tuple, each" \
        "element of which must be an (offset, Colour) tuple."
        for offset, colour in stops :
            self.add_colour_stop(offset, colour)
        #end for
        return \
            self
    #end add_colour_stops

    @property
    def colour_stops(self) :
        "a tuple of the currently-defined (offset, Colour) colour stops. This must" \
        " be a gradient Pattern."
        count = ct.c_int()
        check(cairo.cairo_pattern_get_color_stop_count(self._cairobj, ct.byref(count)))
        count = count.value
        result = []
        offset = ct.c_double()
        r = ct.c_double()
        g = ct.c_double()
        b = ct.c_double()
        a = ct.c_double()
        for i in range(count) :
            check(cairo.cairo_pattern_get_color_stop_rgba(self._cairobj, i, ct.byref(offset), ct.byref(r), ct.byref(g), ct.byref(b), ct.byref(a)))
            result.append((offset.value, Colour(r.value, g.value, b.value, a.value)))
        #end for
        return \
            tuple(result)
    #end colour_stops

    @staticmethod
    def create_colour(c) :
        "creates a Pattern that paints the destination with the specified Colour."
        return \
            Pattern(cairo.cairo_pattern_create_rgba(*Colour.from_rgba(c).to_rgba()))
    #end create_rgb

    @property
    def colour(self) :
        "assumes the Pattern is a solid-colour pattern, returns its Colour."
        r = ct.c_double()
        g = ct.c_double()
        b = ct.c_double()
        a = ct.c_double()
        check(cairo.cairo_pattern_get_rgba(self._cairobj, ct.byref(r), ct.byref(g), ct.byref(g), ct.byref(a)))
        return \
            Colour(r.value, g.value, b.value, a.value)
    #end colour

    @staticmethod
    def create_for_surface(surface) :
        if not isinstance(surface, Surface) :
            raise TypeError("surface is not a Surface")
        #end if
        result = Pattern(cairo.cairo_pattern_create_for_surface(surface._cairobj))
        result._surface = surface # to ensure any storage attached to it doesn't go away prematurely
        return \
            result
    #end create_for_surface

    @property
    def surface(self) :
        "assuming there is a Surface for which this Pattern was created, returns the Surface."
        surf = ct.c_void_p()
        check(cairo.cairo_pattern_get_surface(self._cairobj, ct.byref(surf)))
        return \
            Surface(cairo.cairo_surface_reference(surf.value))
    #end surface

    @staticmethod
    def create_linear(p0, p1, colour_stops = None) :
        "creates a linear gradient Pattern that varies between the specified Vector" \
        " points in pattern space. colour_stops is an optional tuple of (offset, Colour)" \
        " to define the colour stops."
        p0 = Vector.from_tuple(p0)
        p1 = Vector.from_tuple(p1)
        result = Pattern(cairo.cairo_pattern_create_linear(p0.x, p0.y, p1.x, p1.y))
        if colour_stops != None :
            result.add_colour_stops(colour_stops)
        #end if
        return \
            result
    #end create_linear

    @property
    def linear_p0(self) :
        "the first Vector point for a linear gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_linear_points(self._cairobj, ct.byref(x), ct.byref(y), None, None))
        return \
            Vector(x.value, y.value)
    #end linear_p0

    @property
    def linear_p1(self) :
        "the second Vector point for a linear gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_linear_points(self._cairobj, None, None, ct.byref(x), ct.byref(y)))
        return \
            Vector(x.value, y.value)
    #end linear_p1

    @staticmethod
    def create_radial(c0, r0, c1, r1, colour_stops = None) :
        "creates a radial gradient Pattern varying between the circle centred at Vector c0," \
        " radius r0 and the one centred at Vector c1, radius r1. colour_stops is an optional" \
        " tuple of (offset, Colour) to define the colour stops."
        c0 = Vector.from_tuple(c0)
        c1 = Vector.from_tuple(c1)
        result = Pattern(cairo.cairo_pattern_create_radial(c0.x, c0.y, r0, c1.x, c1.y, r1))
        if colour_stops != None :
            result.add_colour_stops(colour_stops)
        #end if
        return \
            result
    #end create_radial

    @property
    def radial_c0(self) :
        "the centre of the start circle for a radial gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, ct.byref(x), ct.byref(y), None, None, None, None))
        return \
            Vector(x.value, y.value)
    #end radial_c0

    @property
    def radial_r0(self) :
        "the radius of the start circle for a radial gradient Pattern."
        r = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, ct.byref(r), None, None, None))
        return \
            r.value
    #end radial_r0

    @property
    def radial_c1(self) :
        "the centre of the end circle for a radial gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, None, ct.byref(x), ct.byref(y), None))
        return \
            Vector(x.value, y.value)
    #end radial_c1

    @property
    def radial_r1(self) :
        "the radius of the end circle for a radial gradient Pattern."
        r = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, None, None, None, ct.byref(r)))
        return \
            r.value
    #end radial_r1

    @property
    def extend(self) :
        "how to extend the Pattern to cover a larger area, as a CAIRO.EXTEND_xxx code."
        return \
            cairo.cairo_pattern_get_extend(self._cairobj)
    #end extend

    @extend.setter
    def extend(self, ext) :
        self.set_extend(ext)
    #end extend

    def set_extend(self, ext) :
        "sets a new extend mode. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the extend property."
        cairo.cairo_pattern_set_extend(self._cairobj, ext)
        return \
            self
    #end set_extend

    @property
    def filter(self) :
        "how to resize the Pattern, as a CAIRO.FILTER_xxx code."
        return \
            cairo.cairo_pattern_get_filter(self._cairobj)
    #end filter

    @filter.setter
    def filter(self, filt) :
        self.set_filter(filt)
    #end filter

    def set_filter(self, filt) :
        "sets a new filter mode. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the filter property."
        cairo.cairo_pattern_set_filter(self._cairobj, filt)
        return \
            self
    #end set_filter

    @property
    def matrix(self) :
        "the transformation from user space to Pattern space."
        result = CAIRO.matrix_t()
        cairo.cairo_pattern_get_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end matrix

    @matrix.setter
    def matrix(self, m) :
        self.set_matrix(m)
    #end matrix

    def set_matrix(self, m) :
        "sets a new matrix. Use for method chaining; otherwise, it’s" \
        " probably more convenient to assign to the matrix property."
        m = m.to_cairo()
        cairo.cairo_pattern_set_matrix(self._cairobj, ct.byref(m))
        return \
            self
    #end set_matrix

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

    # TODO: Raster Sources <http://cairographics.org/manual/cairo-Raster-Sources.html>

#end Pattern

class MeshPattern(Pattern) :
    "a Cairo tensor-product mesh pattern. Do not instantiate directly; use the create" \
    " method."
    # could let user instantiate directly, but having a create method
    # seems more consistent with behaviour of most other wrapper objects
    # (including superclass).

    __slots__ = () # to forestall typos

    @staticmethod
    def create() :
        "creates a new, empty MeshPattern."
        return \
            MeshPattern(cairo.cairo_pattern_create_mesh())
    #end create

    def begin_patch(self) :
        "starts defining a new patch for the MeshPattern. The sides of the patch" \
        " must be defined by one move_to followed by up to 4 line_to/curve_to calls."
        cairo.cairo_mesh_pattern_begin_patch(self._cairobj)
        self._check()
        return \
            self
    #end begin_patch

    def end_patch(self) :
        "finishes defining a patch for the MeshPattern."
        cairo.cairo_mesh_pattern_end_patch(self._cairobj)
        self._check()
        return \
            self
    #end end_patch

    def move_to(self, p) :
        "move_to(p) or move_to((x, y)) -- defines the start point for the sides of the patch."
        p = Vector.from_tuple(p)
        cairo.cairo_mesh_pattern_move_to(self._cairobj, p.x, p.y)
        self._check()
        return \
            self
    #end move_to

    def line_to(self, p) :
        "line_to(p) or line_to((x, y)) -- defines a straight-line side for the current patch."
        p = Vector.from_tuple(p)
        cairo.cairo_mesh_pattern_line_to(self._cairobj, p.x, p.y)
        self._check()
        return \
            self
    #end line_to

    def curve_to(self, p1, p2, p3) :
        "curve_to(p1, p2, p3) or curve_to((x1, y1), (x2, y2), (x3, y3))" \
        " -- defines a curved side for the current patch."
        p1 = Vector.from_tuple(p1)
        p2 = Vector.from_tuple(p2)
        p3 = Vector.from_tuple(p3)
        cairo.cairo_mesh_pattern_curve_to(self._cairobj, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
        self._check()
        return \
            self
    #end curve_to

    def set_control_point(self, point_num, p) :
        "defines an interior control point, where point_num must be an integer in [0 .. 3]." \
        " Changing these from the default turns a Coons patch into a general tensor-product patch."
        p = Vector.from_tuple(p)
        cairo.cairo_mesh_pattern_set_control_point(self._cairobj, point_num, p.x, p.y)
        self._check()
        return \
            self
    #end set_control_point

    def set_corner_colour(self, corner_num, c) :
        "defines the Colour at one of the corners, where corner_num must be an integer" \
        " in [0 .. 3]. Any colours not set default to Colour.grey(0, 0)."
        c = Colour.from_rgba(c)
        cairo.cairo_mesh_pattern_set_corner_color_rgba(self._cairobj, corner_num, c.r, c.g, c.b, c.a)
        self._check()
        return \
            self
    #end set_corner_colour

    @property
    def patch_count(self) :
        "the count of patches defined for the MeshPattern."
        result = ct.c_uint()
        check(cairo.cairo_mesh_pattern_get_patch_count(self._cairobj, ct.byref(result)))
        return \
            result.value
    #end patch_count

    def get_path(self, patch_num) :
        "returns a Path defining the sides of the specified patch_num in [0 .. patch_count - 1]."
        temp = cairo.cairo_mesh_pattern_get_path(self._cairobj, patch_num)
        try :
            result = Path.from_cairo(temp)
        finally :
            cairo.cairo_path_destroy(temp)
        #end try
        return \
            result
    #end get_path

    def get_control_point(self, patch_num, point_num) :
        "returns a Vector for one of the interior control points of the specified" \
        " patch_num in [0 .. patch_count - 1], point_num in [0 .. 3]."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_mesh_pattern_get_control_point(self._cairobj, patch_num, point_num, ct.byref(x), ct.byref(y)))
        return \
            Vector(x.value, y.value)
    #end get_control_point

    def get_corner_colour(self, patch_num, corner_num) :
        "returns a Colour for one of the corners of the specified" \
        " patch_num in [0 .. patch_count - 1], corner_num in [0 .. 3]."
        r = ct.c_double()
        g = ct.c_double()
        b = ct.c_double()
        a = ct.c_double()
        check(cairo.cairo_mesh_pattern_get_corner_color_rgba(self._cairobj, patch_num, corner_num, ct.byref(r), ct.byref(g), ct.byref(b), ct.byref(a)))
        return \
            Colour(r.value, g.value, b.value, a.value)
    #end get_corner_colour

#end MeshPattern

# TODO: Regions <http://cairographics.org/manual/cairo-Regions.html>

class Path :
    "a high-level representation of a Cairo path_t. Instantiate with a sequence" \
    " of Path.Element subclass instances."

    # Unfortunately I cannot provide a to_cairo method, because there is no
    # public Cairo call for allocating a cairo_path_data_t structure. So
    # the conversion from Cairo is one-way, and I have to implement all
    # the drawing from then on.

    __slots__ = ("elements",) # to forestall typos

    class Element :
        "base class for Path elements. Do not instantiate directly;" \
        " instantiate subclasses intead."

        __slots__ = ("type", "points", "meth")

        def __init__(self, type, points, meth) :
            # type is CAIRO.PATH_xxxx code, points is tuple of points,
            # meth is Context instance method to draw the Element
            self.type = type
            self.points = tuple(Vector.from_tuple(p) for p in points)
            self.meth = meth
        #end __init__

        def transform(self, matrix) :
            "returns a copy of the Element with control points transformed" \
            " by the specified Matrix."
            return \
                type(self)(*matrix.mapiter(self.points))
        #end transform

        def draw(self, g, matrix = None) :
            "draws the element into the Context g, optionally transformed by the matrix."
            if matrix != None :
                p = tuple(matrix.mapiter(self.points))
            else :
                p = self.points
            #end if
            self.meth(*((g,) + p))
        #end draw

        def __repr__(self) :
            return \
                "%s(%s)" % (self.__class__.__name__, ", ".join(repr(tuple(p)) for p in self.points))
        #end __repr__

    #end Element

    class MoveTo(Element) :
        "represents a move_to the specified Vector position."

        def __init__(self, p) :
            super().__init__(CAIRO.PATH_MOVE_TO, (p,), Context.move_to)
        #end __init__

    #end MoveTo

    class LineTo(Element) :
        "represents a line_to the specified Vector position."

        def __init__(self, p) :
            super().__init__(CAIRO.PATH_LINE_TO, (p,), Context.line_to)
        #end __init__

    #end LineTo

    class CurveTo(Element) :
        "represents a curve_to via the specified three Vector positions."

        def __init__(self, p1, p2, p3) :
            super().__init__(CAIRO.PATH_CURVE_TO, (p1, p2, p3), Context.curve_to)
        #end __init__

    #end CurveTo

    class Close(Element) :
        "represents a closing of the current path."

        def __init__(self) :
            super().__init__(CAIRO.PATH_CLOSE_PATH, (), Context.close_path)
        #end __init__

    #end Close

    element_types = \
        { # number of control points and Element subclass for each path element type
            CAIRO.PATH_MOVE_TO : {"nr" : 1, "type" : MoveTo},
            CAIRO.PATH_LINE_TO : {"nr" : 1, "type" : LineTo},
            CAIRO.PATH_CURVE_TO : {"nr" : 3, "type" : CurveTo},
            CAIRO.PATH_CLOSE_PATH : {"nr" : 0, "type" : Close},
        }

    def __init__(self, elements) :
        self.elements = []
        for element in elements :
            if not isinstance(element, Path.Element) :
                raise TypeError("path element is not a Path.Element")
            #end if
            self.elements.append(element)
        #end for
    #end __init__

    @classmethod
    def from_cairo(celf, path) :
        "translates a CAIRO.path_data_t to a Path."
        elements = []
        data = ct.cast(path, CAIRO.path_ptr_t).contents.data
        nrelts = ct.cast(path, CAIRO.path_ptr_t).contents.num_data
        i = 0
        while True :
            if i == nrelts :
                break
            i += 1
            header = ct.cast(data, CAIRO.path_data_t.header_ptr_t).contents
            assert header.length == celf.element_types[header.type]["nr"] + 1, "expecting %d control points for path elt type %d, got %d" % (celf.element_types[header.type]["nr"] + 1, header.type, header.length)
            data += ct.sizeof(CAIRO.path_data_t)
            points = []
            for j in range(header.length - 1) :
                assert i < nrelts, "buffer overrun"
                i += 1
                point = ct.cast(data, CAIRO.path_data_t.point_ptr_t).contents
                points.append((point.x, point.y))
                data += ct.sizeof(CAIRO.path_data_t)
            #end for
            elements.append(celf.element_types[header.type]["type"](*points))
        #end for
        return \
            Path(elements)
    #end from_cairo

    def draw(self, ctx, matrix = None) :
        "draws the Path into a Context."
        if not isinstance(ctx, Context) :
            raise TypeError("ctx must be a Context")
        #end if
        for element in self.elements :
            element.draw(ctx, matrix)
        #end for
    #end draw

    def transform(self, matrix) :
        "returns a copy of this Path with elements transformed by the given Matrix."
        return \
            Path \
              (
                element.transform(matrix) for element in self.elements
              )
    #end transform

#end Path

class FontOptions :
    "Cairo font options. Instantiate with no arguments to create a new font_options_t object."
    # <http://cairographics.org/manual/cairo-cairo-font-options-t.html>

    __slots__ = ("_cairobj",) # to forestall typos

    def _check(self) :
        # check for error from last operation on this FontOptions.
        check(cairo.cairo_font_options_status(self._cairobj))
    #end _check

    def __init__(self, existing = None) :
        if existing == None :
            self._cairobj = cairo.cairo_font_options_create()
        else :
            self._cairobj = existing
        #end if
        self._check()
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_font_options_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def copy(self) :
        "returns a copy of this FontOptions in a new object."
        return \
            FontOptions(cairo.cairo_font_options_copy(self._cairobj))
    #end copy

    def merge(self, other) :
        "merges non-default options from another FontOptions object."
        if not isinstance(other, FontOptions) :
            raise TypeError("can only merge with another FontOptions object")
        #end if
        cairo.cairo_font_options_merge(self._cairobj, other._cairobj)
        self._check()
    #end merge

    def __eq__(self, other) :
        "equality of settings in two FontOptions objects."
        if not isinstance(other, FontOptions) :
            raise TypeError("can only compare equality with another FontOptions object")
        #end if
        return \
            cairo.cairo_font_options_equal(self._cairobj, other._cairobj)
    #end __eq__

    @property
    def antialias(self) :
        "antialias mode for this FontOptions."
        return \
            cairo.cairo_font_options_get_antialias(self._cairobj)
    #end antialias

    @antialias.setter
    def antialias(self, anti) :
        cairo.cairo_font_options_set_antialias(self._cairobj, anti)
    #end antialias

    @property
    def subpixel_order(self) :
        "subpixel order for this FontOptions."
        return \
            cairo.cairo_font_options_get_subpixel_order(self._cairobj)
    #end subpixel_order

    @subpixel_order.setter
    def subpixel_order(self, sub) :
        cairo.cairo_font_options_set_subpixel_order(self._cairobj, sub)
    #end subpixel_order

    @property
    def hint_style(self) :
        "hint style for this FontOptions."
        return \
            cairo.cairo_font_options_get_hint_style(self._cairobj)
    #end hint_style

    @hint_style.setter
    def hint_style(self, hint) :
        cairo.cairo_font_options_set_hint_style(self._cairobj, hint)
    #end hint_style

    @property
    def hint_metrics(self) :
        "hint metrics for this FontOptions."
        return \
            cairo.cairo_font_options_get_hint_metrics(self._cairobj)
    #end hint_metrics

    @hint_metrics.setter
    def hint_metrics(self, hint) :
        cairo.cairo_font_options_set_hint_metrics(self._cairobj, hint)
    #end hint_metrics

    def __repr__(self) :
        return \
            (
                "FontOptions({%s})"
            %
                ", ".join
                  (
                    "%s = %d" % (name, getattr(self, name))
                    for name in ("antialias", "subpixel_order", "hint_style", "hint_metrics")
                  )
            )
    #end __repr__

#end FontOptions

class FontFace :
    "a general Cairo font object. Do not instantiate directly; use the create methods."
    # <http://cairographics.org/manual/cairo-cairo-font-face-t.html>

    __slots__ = ("_cairobj", "_user_data") # to forestall typos

    def _check(self) :
        # check for error from last operation on this FontFace.
        check(cairo.cairo_font_face_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
        self._user_data = {}
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_font_face_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def __eq__(self, other) :
        "do the two FontFace objects refer to the same FontFace. Needed because" \
        " ScaledFont.font_face cannot return the same FontFace object each time."
        return \
            isinstance(other, FontFace) and self._cairobj == other._cairobj
    #end __eq__

    @property
    def type(self) :
        "the type of font underlying this FontFace."
        return \
            cairo.cairo_font_face_get_type(self._cairobj)
    #end type

    @staticmethod
    def create_for_file(filename, face_index = 0, load_flags = 0) :
        "uses FreeType to load a font from the specified filename, and returns" \
        " a new FontFace for it."
        _ensure_ft()
        ft_face = ct.c_void_p()
        status = ft.FT_New_Face(ct.c_void_p(ft_lib), filename.encode("utf-8"), face_index, ct.byref(ft_face))
        if status != 0 :
            raise RuntimeError("Error %d loading FreeType font" % status)
        #end if
        try :
            cairo_face = cairo.cairo_ft_font_face_create_for_ft_face(ft_face.value, load_flags)
            result = FontFace(cairo_face)
            check(cairo.cairo_font_face_set_user_data
              (
                cairo_face,
                ct.byref(ft_destroy_key),
                ft_face.value,
                ft.FT_Done_Face
              ))
            ft_face = None # so I don't free it yet
        finally :
            if ft_face != None :
                ft.FT_Done_Face(ft_face)
            #end if
        #end try
        return \
            result
    #end create_for_file

    @staticmethod
    def create_for_pattern(pattern, options = None) :
        "uses Fontconfig to find a font matching the specified pattern string," \
        " uses FreeType to load the font, and returns a new FontFace for it." \
        " options, if present, must be a FontOptions object."
        _ensure_ft()
        _ensure_fc()
        if options != None and not isinstance(options, FontOptions) :
            raise TypeError("options must be a FontOptions")
        #end if
        with _FcPatternManager() as patterns :
            search_pattern = patterns.collect(fc.FcNameParse(pattern.encode("utf-8")))
            if search_pattern == None :
                raise RuntimeError("cannot parse FontConfig name pattern")
            #end if
            if not fc.FcConfigSubstitute(None, search_pattern, _FC.FcMatchPattern) :
                raise RuntimeError("cannot substitute Fontconfig configuration")
            #end if
            if options != None :
                cairo_ft_font_options_substitute(search_pattern, options._cairobj)
            #end if
            fc.FcDefaultSubstitute(search_pattern)
            match_result = ct.c_int()
            found_pattern = patterns.collect(fc.FcFontMatch(None, search_pattern, ct.byref(match_result)))
            if found_pattern == None or match_result.value != _FC.FcResultMatch :
                raise RuntimeError("Fontconfig cannot match font name")
            #end if
            cairo_face = cairo.cairo_ft_font_face_create_for_pattern(found_pattern)
        #end with
        return \
            FontFace(cairo_face)
    #end create_for_pattern

    # TODO: synthesize

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

    # toy font face functions from <http://cairographics.org/manual/cairo-text.html>

    @staticmethod
    def toy_create(family, slant, weight) :
        "creates a “toy” FontFace."
        return \
            FontFace(cairo.cairo_toy_font_face_create(family.encode("utf-8"), slant, weight))
    #end toy_create

    @property
    def toy_family(self) :
        "the family name (only for “toy” fonts)"
        result = cairo.cairo_toy_font_face_get_family(self._cairobj)
        self._check()
        return \
            result.decode("utf-8")
    #end toy_family

    @property
    def toy_slant(self) :
        "the slant setting (only for “toy” fonts)"
        result = cairo.cairo_toy_font_face_get_slant(self._cairobj)
        self._check()
        return \
            result
    #end toy_slant

    @property
    def toy_weight(self) :
        "the weight setting (only for “toy” fonts)"
        result = cairo.cairo_toy_font_face_get_weight(self._cairobj)
        self._check()
        return \
            result
    #end toy

#end FontFace

class ScaledFont :
    "a representation of a Cairo scaled_font_t, which is a font with particular" \
    " size and option settings. Do not instantiate directly; use the create method," \
    " or get one from Context.scaled_font."

    __slots__ = ("_cairobj", "_user_data") # to forestall typos

    def _check(self) :
        # check for error from last operation on this ScaledFont.
        check(cairo.cairo_scaled_font_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
        self._user_data = {}
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_scaled_font_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    @staticmethod
    def create(font_face, font_matrix, ctm, options) :
        "creates a ScaledFont from the specified FontFace, Matrix font_matrix" \
        " and ctm, and FontOptions options."
        # Q: Are any of these optional?
        # A: Looking at Cairo source file src/cairo-scaled-font.c, No.
        if not isinstance(font_face, FontFace) :
            raise TypeError("font_face must be a FontFace")
        #end if
        if not isinstance(font_matrix, Matrix) or not isinstance(ctm, Matrix) :
            raise TypeError("font_matrix and ctm must be Matrix objects")
        #end if
        if not isinstance(options, FontOptions) :
            raise TypeError("options must be a FontOptions")
        #end if
        font_matrix = font_matrix.to_cairo()
        ctm = ctm.to_cairo()
        return \
            ScaledFont(cairo.cairo_scaled_font_create(font_face._cairobj, ct.byref(font_matrix), ct.byref(ctm), options._cairobj))
    #end create

    @property
    def font_extents(self) :
        "returns a FontExtents object giving information about the font settings."
        result = CAIRO.font_extents_t()
        cairo.cairo_scaled_font_extents(self._cairobj, ct.byref(result))
        return \
            FontExtents.from_cairo(result)
    #end font_extents

    def text_extents(self, text) :
        "returns a TextExtents object giving information about drawing the" \
        " specified text at the font settings."
        result = CAIRO.text_extents_t()
        cairo.cairo_scaled_font_text_extents(self._cairobj, text.encode("utf-8"), ct.byref(result))
        return \
            TextExtents.from_cairo(result)
    #end text_extents

    def glyph_extents(self, glyphs) :
        "returns a TextExtents object giving information about drawing the" \
        " specified glyphs at the font settings."
        buf, nr_glyphs = glyphs_to_cairo(glyphs)
        result = CAIRO.text_extents_t()
        cairo.cairo_scaled_font_glyph_extents(self._cairobj, buf, nr_glyphs, ct.byref(result))
        return \
            TextExtents.from_cairo(result)
    #end glyph_extents

    @property
    def font_face(self) :
        return \
            FontFace(cairo.cairo_scaled_font_get_font_face(self._cairobj))
    #end font_face

    @property
    def font_options(self) :
        "a copy of the font options."
        result = FontOptions()
        cairo.cairo_scaled_font_get_font_options(self._cairobj, result._cairobj)
        return \
            result
    #end font_options

    @property
    def font_matrix(self) :
        "the font matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_scaled_font_get_font_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end font_matrix

    @property
    def ctm(self) :
        "the transformation matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_scaled_font_get_ctm(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end ctm

    @property
    def scale_matrix(self) :
        "the scale matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_scaled_font_get_scale_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end scale_matrix

    @property
    def type(self) :
        "the type of font underlying this FontFace."
        return \
            cairo.cairo_scaled_font_get_type(self._cairobj)
    #end type

    @property
    def user_data(self) :
        "a dict, initially empty, which may be used by caller for any purpose."
        return \
            self._user_data
    #end user_data

    # Cairo user_data not exposed to caller, probably not useful

#end ScaledFont

# TODO: user fonts

FontExtents = def_struct_class \
  (
    name = "FontExtents",
    ctname = "font_extents_t"
  )
TextExtents = def_struct_class \
  (
    name = "TextExtents",
    ctname = "text_extents_t"
  )

del def_struct_class # my work is done
