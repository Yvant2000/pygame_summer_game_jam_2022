#include <Python.h>
#include <cmath>
#include <cfloat>

#define M_PI 3.14159265358979323846f
// #define FLT_MAX 3.402823466e+38f
#define EPSILON 0.001f

#define RED 0
#define GREEN -1
#define BLUE -2
#define ALPHA 1

#define P_RED 3
#define P_GREEN 2
#define P_BLUE 1
#define P_ALPHA 0

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

typedef struct t_RayCasterObject{
    PyObject_HEAD
    struct Surface *surfaces = nullptr;
} RayCasterObject;

typedef struct vec3 {
    /*
        y
        |  z
        | /
        O --- x
    */
    float x;
    float y;
    float z;
} vec3;

struct pos2 {
    /* For a segment, the start point and end point.
        A [---------] B
    */
    /* For a line, a point and a direction.
        ------ A ------ B ->
    */
    vec3 A;
    vec3 B;
};

struct pos3 {
    /* For a rectangle, the two opposite corners and the normal
        A ------ *
        |  C ->  |
        * ------ B
    */
    vec3 A;
    vec3 B;
    vec3 C;
};

struct Surface {
    struct pos3 pos;
    vec3 bc;
    bool del;
    struct Surface *next;
    Py_buffer buffer;
    PyObject *parent;
};

inline void free_surface(struct Surface *surface) {
    PyBuffer_Release(&(surface->buffer));
    Py_DECREF(surface->parent);
    free(surface);
}

inline void free_temp_surfaces(struct Surface **surfaces) {
    /*
     * Takes a double ptr surfaces and remove from the chained list all surfaces
     * that have the "del" attribute set to true.
     * When a surface is removed, it needs to be freed with the free_surface function.
     * If the new list is empty, surfaces is set to nullptr.
     */

    struct Surface *prev = nullptr;
    struct Surface *next;
    for (struct Surface *current = *surfaces; current != nullptr; current = next) {
        next = current->next;
        if (current->del) {
            free_surface(current);
            if (prev == nullptr)
                *surfaces = next;
            else
                prev->next = next;
        } else
            prev = current;
    }

}

// static struct Surface *SURFACES = nullptr;

inline vec3 vec3_add(vec3 a, vec3 b) {
    vec3 result = {a.x + b.x, a.y + b.y, a.z + b.z};
    return result;
}

inline vec3 vec3_sub(vec3 a, vec3 b) {
    vec3 result = {a.x - b.x, a.y - b.y, a.z - b.z};
    return result;
}

inline float vec3_dot(vec3 a, vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline vec3 vec3_dot_float(vec3 a, float b) {
    vec3 result = {a.x * b, a.y * b, a.z * b};
    return result;
}

inline vec3 vec3_cross(vec3 a, vec3 b) {
    vec3 result = {a.y * b.z - a.z * b.y,
                   a.z * b.x - a.x * b.z,
                   a.x * b.y - a.y * b.x};
    return result;
}

inline double vec3_length(vec3 a) {
    return sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
}

inline float vec3_dist(vec3 a, vec3 b) {
    return sqrtf(powf(a.x - b.x, 2) + powf(a.y - b.y, 2) + powf(a.z - b.z, 2));
}

inline void get_norm_of_plane(vec3 A, vec3 B, vec3 C, vec3 *norm) {

    vec3 AC = vec3_sub(A, C);
    vec3 BC = vec3_sub(B, C);

    *norm = vec3_cross(AC, BC);
}


inline bool line_plane_collision(vec3 plane_point, vec3 plane_normal,
                                 vec3 line_point, vec3 line_direction,
                                 vec3* intersection) {
    /*
        Compute the intersection of a line and a plane.
        The line is defined by a point and a direction
        The plane is defined by a point and a normal
        The intersection is the point (vec3) where the line intersects the plane

        @return: true if the line intersects the plane, false otherwise
    */
    float normal_dot_direction = vec3_dot(plane_normal, line_direction);
    if (abs(normal_dot_direction) < EPSILON)
        return false; // The line is parallel to the plane.

    vec3 w = vec3_sub(line_point, plane_point);
    float fac = -vec3_dot(plane_normal, w) / normal_dot_direction;
    if (fac < 0 || fac > 1) // The intersection is outside the segment
        return false;
    *intersection = vec3_add(
                        line_point,
                        vec3_dot_float(
                            line_direction,
                            fac)
                        );

    return true;
}

inline bool segment_plane_collision(struct pos3 plane, struct pos2 segment,
                                    vec3 *intersection, float *distance) {
/*
    Compute the intersection of a segment and a surface.
    @param segment: the segment
    The segment is defined by it's start point, a direction/end point
        segment.A = point
        segment.B = direction
    @param plane: the surface
    The surface is defined by it's start point, an end point and a normal.
        plane.A = point
        plane.B = end point
        plane.C = normal
    @param intersection: the point where the segment intersects the plane
    The intersection is set if the line intersects with the plane, even if
    the segment does not intersect with the surface.
        intersection.(x,y,z) = point

    @return: true if the segment intersects the surface, false otherwise
*/
    if (!line_plane_collision(plane.A, plane.C, segment.A, segment.B, intersection))
        return false; // The segment is parallel to the plane.

    *distance = vec3_dist(segment.A, *intersection);

    if (*distance > vec3_length(segment.B))
        return false; // The intersection is outside the segment.

    if (*distance < EPSILON)
        return false; // The distance is null.

    vec3 i = *intersection;
    // Now we need to check if the intersection is between the surface's points.
    if (
        (EPSILON < plane.A.x-i.x && EPSILON < plane.B.x-i.x) || (i.x-plane.A.x > EPSILON && i.x-plane.B.x > EPSILON)
        || (EPSILON < plane.A.y-i.y && EPSILON < plane.B.y-i.y) || (i.y-plane.A.y > EPSILON && i.y-plane.B.y > EPSILON)
        || (EPSILON < plane.A.z-i.z && EPSILON < plane.B.z-i.z) || (i.z-plane.A.z > EPSILON && i.z-plane.B.z > EPSILON)
       )
        return false; // The intersection is outside the surface.

//    vec3 end = vec3_add(segment.A, segment.B);
//    if (
//        (i.x < segment.A.x && i.x < end.x) || (i.x > segment.A.x && i.x > end.x)
//        || (i.y < segment.A.y && i.y < end.y) || (i.y > segment.A.y && i.y > end.y)
//        || (i.z < segment.A.z && i.z < end.z) || (i.z > segment.A.z && i.z > end.z)
//       )
//        return false; // The intersection is outside the segment

    return true;

}

/*
inline bool get_pixel(struct Surface *surface, vec3 point, long *pixel) {

    vec3 ab = vec3_sub(surface->bc, surface->pos.A);
    vec3 av = vec3_sub(point, surface->pos.A);

    double x_dist = vec3_length(vec3_cross(ab, av)) / vec3_length(ab);

    vec3 bc = vec3_sub(surface->pos.B, surface->bc);
    vec3 bv = vec3_sub(point, surface->bc);

    double y_dist = vec3_length(vec3_cross(bc, bv)) / vec3_length(bc);

    float x_len = vec3_dist(surface->bc, surface->pos.B);
    float y_len = vec3_dist(surface->bc, surface->pos.A);

    Py_ssize_t width = surface->buffer.shape[0];
    Py_ssize_t height = surface->buffer.shape[1];

    Py_ssize_t x = (Py_ssize_t)(x_dist * width / x_len);
    Py_ssize_t y = height - (Py_ssize_t)(y_dist * height / y_len);
//    if (x >= width || y >= height)
//        return false;

    long *buf = (long *)surface->buffer.buf;
    *pixel = buf[y * width + x];

    return true;
}
*/

inline unsigned char *get_pixel_3d(struct Surface *surface, vec3 point) {
    vec3 ab = vec3_sub(surface->bc, surface->pos.A);
    vec3 av = vec3_sub(point, surface->pos.A);

    double x_dist = vec3_length(vec3_cross(ab, av)) / vec3_length(ab);

    vec3 bc = vec3_sub(surface->pos.B, surface->bc);
    vec3 bv = vec3_sub(point, surface->bc);

    double y_dist = vec3_length(vec3_cross(bc, bv)) / vec3_length(bc);

    float x_len = vec3_dist(surface->bc, surface->pos.B);
    float y_len = vec3_dist(surface->bc, surface->pos.A);

    Py_ssize_t width = surface->buffer.shape[0];
    Py_ssize_t height = surface->buffer.shape[1];

    Py_ssize_t x = (Py_ssize_t)(x_dist * width / x_len);
    Py_ssize_t y = height - (Py_ssize_t)(y_dist * height / y_len);

    if (x >= width || y >= height)
        return nullptr;

    long *buf = (long *)surface->buffer.buf;
    long *pixel = buf + (y * width + x);

    return (unsigned char*) pixel;
}


/*
inline bool get_closest_surface(struct pos2 ray, float *dist, struct Surface **surf, vec3 *point, struct Surface *surface) {
    float min_distance = FLT_MAX;
    for (; surface != nullptr; surface = surface->next) {
        vec3 intersection;
        float distance;
        if (!segment_plane_collision(surface->pos, ray, &intersection, &distance))
            continue;

        if (distance >= min_distance)
            continue;

        min_distance = distance;
        *surf = surface;
        *point = intersection;
    }
    if (min_distance == FLT_MAX)
        return false;
    *dist = min_distance;
    return true;
}
*/




inline unsigned long get_pixel_sum(struct pos2 ray, struct Surface *surface) {
    unsigned long pixel = 0;

    int alpha_sum = 0;
    unsigned char *pixel_ptr = (unsigned char*)&pixel;
    float min_distance = FLT_MAX;
    for (; surface != nullptr; surface = surface->next) {

        vec3 intersection;
        float distance;
        if (!segment_plane_collision(surface->pos, ray, &intersection, &distance))
            continue;

        bool far = distance >= min_distance;

        if (pixel_ptr[P_ALPHA] == 255 && far)
            continue;

        unsigned char *new_pixel_ptr = get_pixel_3d(surface, intersection);

        if (new_pixel_ptr == nullptr || new_pixel_ptr[ALPHA] == 0)
            continue;

        if (!far){
            min_distance = distance;
            if (new_pixel_ptr[ALPHA] == 255){
                pixel = *((unsigned long *)(new_pixel_ptr - 3));
                alpha_sum = 255;
                continue;
            }
        }

        alpha_sum += new_pixel_ptr[ALPHA];

        float alpha_factor = (float)pixel_ptr[P_ALPHA] / alpha_sum;
        float alpha_factor2 = (float)new_pixel_ptr[ALPHA] / alpha_sum;

        pixel_ptr[P_ALPHA] += (unsigned char)(alpha_factor2 - alpha_factor);
        pixel_ptr[P_BLUE] += (unsigned char)(new_pixel_ptr[BLUE] * alpha_factor2 - pixel_ptr[P_BLUE] * alpha_factor );
        pixel_ptr[P_GREEN] += (unsigned char)(new_pixel_ptr[GREEN] * alpha_factor2 - pixel_ptr[P_GREEN] * alpha_factor);
        pixel_ptr[P_RED] += (unsigned char)(new_pixel_ptr[RED] * alpha_factor2 - pixel_ptr[P_RED] * alpha_factor);

//        pixel_ptr[P_ALPHA] += (new_pixel_ptr[ALPHA] - pixel_ptr[P_ALPHA]) / alpha_sum;
//        pixel_ptr[P_BLUE] += new_pixel_ptr[BLUE] * new_pixel_ptr[ALPHA] / alpha_sum;
//        pixel_ptr[P_GREEN] += new_pixel_ptr[GREEN] * new_pixel_ptr[ALPHA] / alpha_sum;
//        pixel_ptr[P_RED] += new_pixel_ptr[RED] * new_pixel_ptr[ALPHA] / alpha_sum;
    }
    pixel_ptr[P_ALPHA] = 0;

    return pixel;
}

/*
inline bool _get_buffer_from_Surface(PyObject *img, Py_buffer *buffer) {
//
//        Get the buffer from a pygame surface.
//        @param img: the surface
//        @param buffer: the buffer
//        @return: true on error, false on success
//
    PyObject * get_view_method = PyObject_GetAttrString(img, "get_view");
    if (get_view_method == NULL)
        return true;

    PyObject * view = PyObject_CallNoArgs(get_view_method);

    Py_DECREF(get_view_method);

    if (PyObject_GetBuffer(view, buffer, PyBUF_STRIDES) == -1) {
        Py_DECREF(view);
        return true;
    }

    Py_DECREF(view);

    return false;
}
*/
inline bool _get_3DBuffer_from_Surface(PyObject *img, Py_buffer *buffer) {
    PyObject * get_view_method = PyObject_GetAttrString(img, "get_view");
    if (get_view_method == NULL) {
        return true;
    }

    PyObject *arg = Py_BuildValue("y", "3");
    PyObject * view = PyObject_CallOneArg(get_view_method, arg); // array of width * height * RGBA

    Py_DECREF(arg);
    Py_DECREF(get_view_method);

    if (PyObject_GetBuffer(view, buffer, PyBUF_STRIDES) == -1) {
        Py_DECREF(view);
        return true;
    }

    Py_DECREF(view);

    return false;
}


static PyObject *method_add_surface(RayCasterObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *surface_image;

    float A_x;
    float A_y;
    float A_z;

    float B_x;
    float B_y;
    float B_z;

    float C_x = FP_NAN;
    float C_y = FP_NAN;
    float C_z = FP_NAN;

    bool del = false;

    static char *kwlist[] = {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Offffff|fffp", kwlist,
                                     &surface_image, &A_x, &A_y, &A_z, &B_x, &B_y, &B_z, &C_x, &C_y, &C_z, &del))
        return NULL;

    struct Surface *surface = (Surface *) malloc(sizeof(struct Surface));
    surface->pos.A.x = A_x;
    surface->pos.A.y = A_y;
    surface->pos.A.z = A_z;
    surface->pos.B.x = B_x;
    surface->pos.B.y = B_y;
    surface->pos.B.z = B_z;
    surface->parent = surface_image;
    surface->del = del;

    if (_get_3DBuffer_from_Surface(surface_image, &(surface->buffer))) {
        PyErr_SetString(PyExc_ValueError, "Not a valid surface");
        return NULL;
    }
    Py_INCREF(surface_image); // We need to keep the surface alive to make sure the buffer is valid.

    surface->next = self->surfaces; // Push the surface on top of the stack.
    self->surfaces = surface;

    vec3 C;
    if (C_x == FP_NAN || C_y == FP_NAN || C_z == FP_NAN)
        C = {A_x, B_y, A_z}; // define a new vector C bellow A and at the same level as B
    else
        C = {C_x, C_y, C_z};

    surface->bc = C;

    get_norm_of_plane(surface->pos.A, surface->pos.B, C, &(surface->pos.C));

    Py_RETURN_NONE;
}

static PyObject *method_clear_surfaces(RayCasterObject *self) {
    struct Surface *next;
    for (struct Surface *surface = self->surfaces; surface != nullptr; surface = next) {
        next = surface->next;
//        PyBuffer_Release(&(surface->buffer));
//        Py_DECREF(surface->parent);
//        free(surface);
        free_surface(surface);
    }
    self->surfaces = nullptr;
    Py_RETURN_NONE;
}

static PyObject *method_raycasting(RayCasterObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *screen;

    float x = 0.f;
    float y = 0.f;
    float z = 0.f;

    float angle_x = 0.f;
    float angle_y = 0.f;

    float fov = 120.f;
    float view_distance = 1000.f;
    int step = 1;
    //float theta = 1.0f;
    bool rad = false;

    static char *kwlist[] = {"dst_surface", "x", "y", "z", "angle_x", "angle_y", "fov", "view_distance", "step", "rad", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|fffffffip", kwlist,
                                     &screen, &x, &y, &z, &angle_x, &angle_y, &fov, &view_distance, &step, &rad))
        return NULL;

    if(fov <= 0.f) {
        PyErr_SetString(PyExc_ValueError, "fov must be greater than 0");
        return NULL;
    }
    if (view_distance <= 0.f) {
        PyErr_SetString(PyExc_ValueError, "view_distance must be greater than 0");
        return NULL;
    }
//    if (theta <= 0.f) {
//        PyErr_SetString(PyExc_ValueError, "theta must be greater than 0");
//        return NULL;
//    }
    if (step < 1) {
        PyErr_SetString(PyExc_ValueError, "the step must by higher than 0");
        return NULL;
    }

    Py_buffer dst_buffer;
    if (_get_3DBuffer_from_Surface(screen, &dst_buffer)) {
        PyErr_SetString(PyExc_ValueError, "dst_surface is not a valid surface");
        return NULL;
    }

    if (!rad) { // If the given angles are in degrees, convert them to radians.
        angle_x = angle_x * M_PI / 180.f;
        angle_y = angle_y * M_PI / 180.f;
        fov = fov * M_PI / 180.f;
        // theta = theta * M_PI / 180.f;
    }


    // x_angle is the angle of the ray around the x axis.
    // y_angle is the angle of the ray around the y axis.
    /*    y
        < | >   Λ
    ------ ------ x
          |     V
    */
    // It may be confusing because the x_angle move through the y axis,
    // and the y_angle move through the x axis as shown in the diagram.
    struct pos2 ray;
    ray.A.x = x;
    ray.A.y = y;
    ray.A.z = z;

    Py_ssize_t width = dst_buffer.shape[0];
    Py_ssize_t height = dst_buffer.shape[1];

    float d_fov = fov/2;

    long *buf = (long *)dst_buffer.buf;

    float d_theta_x = fov / (float)(height / step);
    float d_theta_y = fov / (float)(width / step);

    float theta_x = d_fov + angle_x;

    for (Py_ssize_t dst_y = 0; dst_y + step <= height; dst_y += step) {
    //for (float theta_x = 0; theta_x < fov; theta_x += theta) {
        //float view_theta_x = theta_x - d_fov + angle_x;
        float view_theta_x = theta_x;
        theta_x -= d_theta_x;
        ray.B.y = view_distance * sinf(view_theta_x);
        float dist_2d = abs(ray.B.y - ray.A.y);
        float hypo = sqrtf(view_distance * view_distance - dist_2d * dist_2d);

        float theta_y = d_fov + angle_y;

        for (Py_ssize_t dst_x = 0; dst_x + step <= width; dst_x += step) {
        //for(float theta_y = 0; theta_y < fov; theta_y += theta) {
            // float view_theta_y = theta_y - d_fov + angle_y;
            float view_theta_y = theta_y;
            theta_y -= d_theta_y;
            ray.B.x = hypo * cosf(view_theta_y);
            ray.B.z = hypo * sinf(view_theta_y);

            /*
            // Check if the ray intersects with any surface.
            // Keep only the closest surface.
            float dist;
            struct Surface *surface = nullptr;
            vec3 intersection;
            if (!get_closest_surface(ray, &dist, &surface, &intersection, self->surfaces))
                continue;

            // Calculate the color of the pixel.
            long pixel;
            get_pixel(surface, intersection, &pixel);
            // Set the pixel in the destination surface.
            // Py_ssize_t dst_x = width - (Py_ssize_t)(theta_y * width / fov );
            // Py_ssize_t dst_y = height - (Py_ssize_t)(theta_x * height / fov );

            //if (dst_x >= width || dst_y >= height)
            //    continue;

            for (Py_ssize_t xp = 0; xp < step; ++xp)
                for (Py_ssize_t yp = 0; yp < step; ++yp)
                    buf[(dst_y+yp) * width + (dst_x+xp)] = pixel;
            */
            unsigned long pixel = get_pixel_sum(ray, self->surfaces);
            if (pixel == 0)
                continue;

            for (Py_ssize_t xp = 0; xp < step; ++xp)
                for (Py_ssize_t yp = 0; yp < step; ++yp)
                    *((unsigned long*)((unsigned char*)(buf + (dst_y+yp) * width + (dst_x+xp)) - 3)) = pixel;
        }
    }

    PyBuffer_Release(&dst_buffer);

    free_temp_surfaces(&(self->surfaces));

    Py_RETURN_NONE;
}





static PyMethodDef CasterMethods[] = {
        {"add_surface", (PyCFunction) method_add_surface, METH_VARARGS | METH_KEYWORDS, "Adds a surface to the caster."},
        {"clear_surfaces", (PyCFunction) method_clear_surfaces, METH_NOARGS, "Clears all surfaces from the caster."},
        {"raycasting", (PyCFunction) method_raycasting, METH_VARARGS | METH_KEYWORDS, "Display the scene using raycasting."},
        {NULL, NULL, 0, NULL}
};

static PyTypeObject RayCasterType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "nostalgiaeraycasting.RayCaster",
        .tp_basicsize = sizeof(RayCasterObject),
        .tp_itemsize = 0,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .tp_doc = PyDoc_STR("RayCaster Object"),
        .tp_methods = CasterMethods,
        .tp_new = PyType_GenericNew,
};


static struct PyModuleDef castermodule = {
    PyModuleDef_HEAD_INIT,
    "nostalgiaeraycasting",
    "Python ray casting module for pygame",
    -1,
};


PyMODINIT_FUNC PyInit_nostalgiaeraycasting(void) {
    if (PyType_Ready(&RayCasterType) < 0)
        return NULL;

    PyObject *m = PyModule_Create(&castermodule);

    if (m == NULL)
        return NULL;

    Py_INCREF(&RayCasterType);
    if (PyModule_AddObject(m, "RayCaster", (PyObject *)&RayCasterType) < 0) {
        Py_DECREF(&RayCasterType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}