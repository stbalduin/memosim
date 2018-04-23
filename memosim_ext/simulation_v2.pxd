import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cdef class Sum(object):
    cpdef public DTYPE_t compute(self, dict attr_inputs)


cdef class OutputAccessor(object):
    cdef public RegressionModelSimulator simulator
    cdef public int idx
    cpdef DTYPE_t run(self)


cdef class ConstantInputAccessor(object):
    cdef DTYPE_t value
    cpdef public DTYPE_t run(self)


cdef class ExternalInputAccessor(object):
    cdef int idx
    cdef RegressionModelSimulator simulator
    cpdef DTYPE_t run(self)


cdef class FeedbackInputAccessor(object):
    cdef int idx
    cdef RegressionModelSimulator simulator
    cpdef DTYPE_t run(self)


cdef class RegressionModelSimulator(object):
    cdef public list input_accessors
    cdef public dict output_accessors
    cdef public np.ndarray state
    cdef public np.ndarray external_inputs
    cdef public np.ndarray _internal_inputs
    cdef public int _num_input_accessors

    cpdef public void init(self, int num_external_inputs, int num_outputs, list input_accessors, dict output_accessors)
    cpdef public void step(self)


cdef class OLSModel(RegressionModelSimulator):
    cdef np.ndarray intercept
    cdef np.ndarray coefs

    cpdef public np.ndarray compute_responses(self, np.ndarray inputs)
