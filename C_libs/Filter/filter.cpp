#include <Python.h>
// #define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
// #include <numpy/arrayobject.h> // remove dependencies

#include <cmath>

#define M_PI 3.14159265358979323846f

#define RED 0
#define GREEN -1
#define BLUE -2


#define D_C_QUOT 1.8f

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

int _get_buffer_from_Surface(PyObject *img, Py_buffer *buffer) {
    PyObject * get_view_method = PyObject_GetAttrString(img, "get_view");
    if (get_view_method == NULL) {
        return -1;
    }

    PyObject * view = PyObject_CallNoArgs(get_view_method); // array of width * height * color

    Py_DECREF(get_view_method);

    if (PyObject_GetBuffer(view, buffer, PyBUF_STRIDES) == -1) {
        Py_DECREF(view);
        return -1;
    }

    Py_DECREF(view);

    return 0;
}

int _get_3DBuffer_from_Surface(PyObject *img, Py_buffer *buffer) {
    PyObject * get_view_method = PyObject_GetAttrString(img, "get_view");
    if (get_view_method == NULL) {
        return -1;
    }

    PyObject *arg = Py_BuildValue("y", "3");
    PyObject * view = PyObject_CallOneArg(get_view_method, arg); // array of width * height * RGBA

    Py_DECREF(arg);
    Py_DECREF(get_view_method);

    if (PyObject_GetBuffer(view, buffer, PyBUF_STRIDES) == -1) {
        Py_DECREF(view);
        return -1;
    }

    Py_DECREF(view);

    return 0;
}

static PyObject *method_color_filter_from_buffer(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject * img;

    bool red = true;
    bool green = true;
    bool blue = true;

    bool magenta = true;
    bool yellow = true;
    bool cyan = true;

    static char *kwlist[] = {"image", "red", "green", "blue", "magenta", "yellow", "cyan", NULL};
    if (!PyArg_ParseTupleAndKeywords( args, kwargs, "O|pppppp", kwlist, &img, &red, &green, &blue, &magenta,&yellow, &cyan))
        return NULL;

    Py_buffer buffer;
    if (_get_3DBuffer_from_Surface(img, &buffer)) {
        printf("image isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    Py_ssize_t width = buffer.shape[0];
    Py_ssize_t height = buffer.shape[1];

    long *buf = (long *) buffer.buf;

//    printf("%d\n", buffer.ndim);
//    for (int i = 0; i < buffer.ndim; i++){
//        printf("%lld\n", buffer.shape[i]);
//        printf("%lld\n", buffer.strides[i]);
//    }
//
//    Py_RETURN_NONE;


    for (Py_ssize_t x = 0; x < width; ++x){

        for(Py_ssize_t y = 0; y < height; ++y){

            unsigned char *pixel = (unsigned char *)(buf + (y * width + x));

            unsigned char b = pixel[BLUE];
            unsigned char g = pixel[GREEN];
            unsigned char r = pixel[RED];

//            printf("0 - %hhu\n", r);
//            printf("-1 - %hhu\n", g);
//            printf("-2 - %hhu\n", b);
//            printf("\n");


            if(red && r > g * D_C_QUOT && r > b * D_C_QUOT) continue; // _red
            if(green && g > r * D_C_QUOT && g > b * D_C_QUOT) continue; // green
            if(blue && b > r * D_C_QUOT && b > g * D_C_QUOT) continue; // blue

            if(magenta && ((r > D_C_QUOT * g && b > g) || (b > D_C_QUOT * g && r > g)) && r <= D_C_QUOT * b && b <= D_C_QUOT * r) continue; // magenta
            if(yellow && ((r > D_C_QUOT * b && g > b) || (g > D_C_QUOT * b && r > b)) && r <= D_C_QUOT * g && g <= D_C_QUOT * r) continue; // yellow
            if(cyan && ((b > D_C_QUOT * r && g > r) || (g > D_C_QUOT * r && b > r)) && g <= D_C_QUOT * b && b <= D_C_QUOT * g) continue; // cyan

            if (red && green && blue &&
                r <= D_C_QUOT * g && r <= D_C_QUOT * b &&
                g <= D_C_QUOT * r && g <= D_C_QUOT * b &&
                b <= D_C_QUOT * r && b <= D_C_QUOT * g)
                continue; // brown

            int _blue = (int)(r * 0.272f + g * 0.504f + b * 0.131f);
            int _green = (int)(r * 0.349f + g * 0.656f + b * 0.168f);
            int _red = (int)(r * 0.393f + g * 0.739f + b * 0.189f);

            pixel[BLUE] = (char)((_blue > 255) ? 255 : _blue);
            pixel[GREEN] = (char)((_green > 255) ? 255 : _green);
            pixel[RED] = (char)((_red > 255) ? 255 : _red);
        }
    }

    PyBuffer_Release(&buffer);
    Py_RETURN_NONE;
}


long distortion_time = 0;

static PyObject *method_distortion_from_buffer(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject * src_img;
    PyObject * dst_img;

    float amplitude = 1.0f;
    float frequency = 1.0f;
    float speed = 1.0f;

    bool vertical_distortion = false;
    bool horizontal_distortion = false;


    static char *kwlist[] = {"src_image", "dst_image", "horizontal_distortion", "vertical_distortion", "amplitude", "frequency", "speed", NULL};
    if (!PyArg_ParseTupleAndKeywords( args, kwargs, "OO|ppfff", kwlist,
                                      &src_img, &dst_img, &horizontal_distortion, &vertical_distortion, &amplitude, &frequency, &speed))
        return NULL;

    Py_buffer src_buf;
    Py_buffer dst_buf;


    if (_get_buffer_from_Surface(src_img, &src_buf)) {
        printf("src_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    if (_get_buffer_from_Surface(dst_img, &dst_buf)) {
        printf("dst_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    Py_ssize_t width = src_buf.shape[0];
    Py_ssize_t height = src_buf.shape[1];
    Py_ssize_t width2 = dst_buf.shape[0];
    Py_ssize_t height2 = dst_buf.shape[1];

    if (width != width2 || height != height2) {
        PyErr_SetString(PyExc_ValueError, "src_img and dst_img must have the same size");
        return NULL;
    }

    long *sbuf = (long *) src_buf.buf;
    long *dbuf = (long *) dst_buf.buf;

    for (Py_ssize_t x = 0; x < width; ++x){
        Py_ssize_t xu = (Py_ssize_t)(x + (horizontal_distortion ? (amplitude * sin( frequency*x + speed*distortion_time )) : 0));
        while (xu < 0)
            xu += width;
        xu = xu % width;

        for(Py_ssize_t y = 0; y < height; ++y){
            Py_ssize_t yu = (Py_ssize_t)(y + (vertical_distortion ? (amplitude * sin( frequency*y + speed*distortion_time )) : 0));
            while (yu < 0)
                yu += height;
            yu = yu % height;

            dbuf[(y * width + x)] = sbuf[(yu * width + xu)];
        }
    }


    PyBuffer_Release(&src_buf);
    PyBuffer_Release(&dst_buf);

    distortion_time++;

    Py_RETURN_NONE;
}

static PyObject *method_vignette(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *src_img;
    float inner_radius = 50.0f;
    float strength = 1.0f;
    PyObject *pos = NULL;

    static char *kwlist[] = {"src_img", "pos", "inner_radius", "strength", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|Off", kwlist, &src_img, &pos, &inner_radius, &strength))
        return NULL;

    float center_x;
    float center_y;

    Py_buffer src_buf;
    if (_get_3DBuffer_from_Surface(src_img, &src_buf)) {
        printf("src_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    Py_ssize_t width = src_buf.shape[0];
    Py_ssize_t height = src_buf.shape[1];

    // By default, the center of the vignette is the center of the image
    if (pos == NULL) {
        center_x = (float)width / 2;
        center_y = (float)height / 2;
    }  // Otherwise, the center of the vignette is the given position
    else if (!PyArg_ParseTuple(pos, "ff", &center_x, &center_y))
        return NULL;

    long *buf = (long *) src_buf.buf;

    for (Py_ssize_t x = 0; x < width; ++x) {
        for (Py_ssize_t y = 0; y < height; ++y) {
            float dist = (float)sqrt(pow(x - center_x, 2) + pow(y - center_y, 2));
            if (dist > inner_radius) {
                float alpha = 1 - strength * ((dist - inner_radius) / ((float)width - inner_radius));
                if (alpha < 0)
                    alpha = 0;

                unsigned char *pixel = (unsigned char *)(buf + (y * width + x));

                pixel[BLUE] = (char)( pixel[BLUE] * alpha );
                pixel[GREEN] = (char)(pixel[GREEN] * alpha);
                pixel[RED] = (char)(pixel[RED] * alpha);
            }
        }
    }

    PyBuffer_Release(&src_buf);

    Py_RETURN_NONE;
}

static PyObject *method_blur(PyObject *self, PyObject *args, PyObject *kwargs) {
    // TODO
    Py_RETURN_NONE;
}

inline bool ccw(float A_x, float A_y,
                float B_x, float B_y,
                float C_x, float C_y) {
    return (C_y - A_y) * (B_x - A_x) > (B_y - A_y) * (C_x - A_x);
}

inline bool _check_segment_intersect(float A_x, float A_y, float B_x, float B_y,
                                     float C_x, float C_y, float D_x, float D_y) {
    return ccw(A_x, A_y, C_x, C_y, D_x, D_y) != ccw(B_x, B_y, C_x, C_y, D_x, D_y) &&
           ccw(A_x, A_y, B_x, B_y, C_x, C_y) != ccw(A_x, A_y, B_x, B_y, D_x, D_y);
}

#define EPSILON 0.00001f

inline bool _segment_intersection(float A_x, float A_y, float B_x, float B_y,
                                  float C_x, float C_y, float D_x, float D_y,
                                  float *intersect_x, float *intersect_z) {
    if (!_check_segment_intersect(A_x, A_y, B_x, B_y, C_x, C_y, D_x, D_y))
        return false;

    float x_diff_1 = A_x - B_x;
    float x_diff_2 = C_x - D_x;
    float y_diff_1 = A_y - B_y;
    float y_diff_2 = C_y - D_y;

    float div = x_diff_1 * y_diff_2 - x_diff_2 * y_diff_1;

    if (abs(div) < EPSILON)
        return false;

    float d_x = A_x * B_y - A_y * B_x;
    float d_y = C_x * D_y - C_y * D_x;

    *intersect_x = (d_x * x_diff_2 - d_y * x_diff_1) / div;
    *intersect_z = (d_x * y_diff_2 - d_y * y_diff_1) / div;

    return true;
}

static PyObject *method_display_surface_in_3D_space(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *src_img;
    PyObject *dst_img;

    float A_x;
    float A_z;

    float B_x;
    float B_z;

    float fov = 60.0f;
    float step = 0.1f;
    float view_dist = 1000.0f;

    bool rad = false;

    static char *kwlist[] = {"src_img", "dst_img",
                             "A_x", "A_z",
                             "B_x", "B_z",
                             "fov", "step", "view_dist", "rad", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOffff|fffb", kwlist,
                                     &src_img, &dst_img,
                                     &A_x, &A_z,
                                     &B_x, &B_z,
                                     &fov, &step, &view_dist, &rad))
        return NULL;

    if (!rad) { // If the angles are in degrees, convert them to radians
        fov = fov * M_PI / 180.0f;
        step = step * M_PI / 180.0f;
    }

    Py_buffer src_buf;
    Py_buffer dst_buf;

    if (_get_buffer_from_Surface(src_img, &src_buf)) {
        printf("src_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    if (_get_buffer_from_Surface(dst_img, &dst_buf)) {
        printf("dst_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    long *sbuf = (long*)src_buf.buf;
    long *dbuf = (long*)dst_buf.buf;

    Py_ssize_t image_width = src_buf.shape[0];
    Py_ssize_t image_height = src_buf.shape[1];

    Py_ssize_t dst_width = dst_buf.shape[0];
    Py_ssize_t dst_height = dst_buf.shape[1];

    double line_length = sqrt(pow(A_x - B_x, 2) + pow(A_z - B_z, 2));
    double src_x_ratio = (double)image_width / line_length;
    double x_ratio = dst_width / (2 * fov);
    float pixel_step = step * dst_width / (2 * fov);

    for (float angle_y = -fov; angle_y < fov; angle_y += step) {
        float cos_angle = cosf(angle_y);
        float sin_angle = sinf(angle_y);

        float view_x = view_dist * cos_angle;
        float view_z = view_dist * sin_angle;

        float intersect_x;
        float intersect_z;
        if (!_segment_intersection(0, 0, view_x, view_z,
                                   A_x, A_z, B_x, B_z,
                                   &intersect_x, &intersect_z))
            continue;

        float dist = (float)sqrt(pow(intersect_x, 2) + pow(intersect_z, 2)) * cos_angle;
        if (dist > view_dist)
            continue;

        double local_dist = sqrt(pow(intersect_x - A_x, 2) + pow(intersect_z - A_z, 2));
        Py_ssize_t src_x = (Py_ssize_t)(local_dist * src_x_ratio);

        double x = (angle_y + fov) * x_ratio;
        Py_ssize_t x_max = (Py_ssize_t)(x + pixel_step);
        Py_ssize_t height = (Py_ssize_t)(dst_height / dist);
        Py_ssize_t delta_height = (dst_height - height) / 2;

        float y_dec = (float)image_height / height;

        for (Py_ssize_t dst_x = (Py_ssize_t)x; dst_x < x_max; ++dst_x)
            if (dst_x < 0 || dst_x >= dst_width)
                continue;
            else
                for (Py_ssize_t y = 0; y < height; ++y) {
                    Py_ssize_t dst_y = delta_height + y;
                    if (dst_y < 0 || dst_y >= dst_height)
                        continue;
                    Py_ssize_t src_y = (Py_ssize_t)(y * y_dec);
                    dbuf[dst_y * dst_width + dst_x] = sbuf[src_y * image_width + src_x];
                }
    }

    PyBuffer_Release(&src_buf);
    PyBuffer_Release(&dst_buf);

    Py_RETURN_NONE;
}

static PyObject *method_mode_seven(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *src_img;
    PyObject *dst_img;

    float x0, y0;  // Origin offset

    float a, b, c, d; // transformation coefficients

    static char *kwlist[] = {"src_img", "dst_img", "x0", "y0", "a", "b", "c", "d", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOffffff", kwlist, &src_img, &dst_img, &x0, &y0, &a, &b, &c, &d))
        return NULL;

    Py_buffer src_buf;
    Py_buffer dst_buf;

    if (_get_buffer_from_Surface(src_img, &src_buf)) {
        printf("src_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    if (_get_buffer_from_Surface(dst_img, &dst_buf)) {
        printf("dst_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    Py_ssize_t width = src_buf.shape[0];
    Py_ssize_t height = src_buf.shape[1];
    Py_ssize_t width2 = dst_buf.shape[0];
    Py_ssize_t height2 = dst_buf.shape[1];

    long *sbuf = (long *) src_buf.buf;
    long *dbuf = (long *) dst_buf.buf;

    for (Py_ssize_t x = 0; x < width; ++x) {
        for (Py_ssize_t y = 0; y < height; ++y) {
            Py_ssize_t x_ = (Py_ssize_t)(a * x - a * x0 + b * y - b * y0 + x0);
            Py_ssize_t y_ = (Py_ssize_t)(c * x - c * x0 + d * y - d * y0 + y0);
            if (x_ < 0 || x_ >= width2 || y_ < 0 || y_ >= height2)
                continue;
            dbuf[(y_ * width2 + x_)] = sbuf[(y * width + x)];
        }
    }

    PyBuffer_Release(&src_buf);
    PyBuffer_Release(&dst_buf);

    Py_RETURN_NONE;
}

static PyObject *method_fish_from_buffer(PyObject *self, PyObject *args) {

    PyObject * src_img;
    PyObject * dst_img;
    float distortion_coefficient;

    if (!PyArg_ParseTuple(args, "OOf", &src_img, &dst_img, &distortion_coefficient))
        return NULL;

    Py_buffer src_buf;
    Py_buffer dst_buf;


    if (_get_buffer_from_Surface(src_img, &src_buf)) {
        printf("src_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    if (_get_buffer_from_Surface(dst_img, &dst_buf)) {
        printf("dst_img isn't a valid Surface\n");
        Py_RETURN_NONE;
    }

    Py_ssize_t width = src_buf.shape[0];
    Py_ssize_t height = src_buf.shape[1];
    Py_ssize_t width2 = dst_buf.shape[0];
    Py_ssize_t height2 = dst_buf.shape[1];

    if (width != width2 || height != height2) {
        PyErr_SetString(PyExc_ValueError, "src_img and dst_img must have the same size");
        return NULL;
    }

    long *sbuf = (long *) src_buf.buf;
    long *dbuf = (long *) dst_buf.buf;

    float minus_width = 2.0f / width;
    float minus_height = 2.0f / height;

    float xn = -1.0f;
    for (Py_ssize_t x = 0; x < width; ++x){
        // float xn = minus_width * x - 1.0f;

        float yn = -1.0f;
        for(Py_ssize_t y = 0; y < height; ++y){
            float xnd = xn;
            float ynd = yn;

            // float ynd = 2.0f / height * y - 1.0f;

            float div = 1.0f - distortion_coefficient * (xnd * xnd + ynd * ynd);
            if (div != 0.0f){
                xnd = xnd / div;
                ynd = ynd / div;
            }

            short xu = (short)(((xnd + 1) / 2.0f) * width);
            short yu = (short)(((ynd + 1) / 2.0f) * height);

            if (0 <= xu && xu < width && 0 <= yu && yu < height)
                dbuf[(y * width + x)] = sbuf[(yu * width + xu)];

            yn += minus_height;
        }
        xn += minus_width;
    }

    PyBuffer_Release(&src_buf);
    PyBuffer_Release(&dst_buf);

    Py_RETURN_NONE;
}



static PyMethodDef FilterMethods[] = {
    {"fish", method_fish_from_buffer, METH_VARARGS, "FishEye effect. Takes a two pygame Surfaces and a float as arguments."},
    {"distortion", (PyCFunction) method_distortion_from_buffer, METH_VARARGS | METH_KEYWORDS, "Earthbound distortion effect"},
    {"color_filter", (PyCFunction) method_color_filter_from_buffer, METH_VARARGS | METH_KEYWORDS, "Color selection. Takes a pygame Surface and color boolean arguments."},
    {"vignette", (PyCFunction) method_vignette, METH_VARARGS | METH_KEYWORDS, "Vignette effect."},
    {"blur", (PyCFunction) method_blur, METH_VARARGS | METH_KEYWORDS, "Blur effect."},
    {"display_in_3D_space", (PyCFunction) method_display_surface_in_3D_space, METH_VARARGS | METH_KEYWORDS, "Display a pygame Surface in 3D space."},
    {"mode_seven", (PyCFunction) method_mode_seven, METH_VARARGS | METH_KEYWORDS, "Mode 7 effect."},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef filtermodule = {
    PyModuleDef_HEAD_INIT,
    "nostalgiaefilters",
    "Python interface for image filter",
    -1,
    FilterMethods
};

PyMODINIT_FUNC PyInit_nostalgiaefilters(void) {
	// import_array()
    return PyModule_Create(&filtermodule);
}