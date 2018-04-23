import numpy as np
cimport numpy as np
cimport cython

import memomodel

DTYPE = np.float64

cdef class Sum(object):

    cpdef public DTYPE_t compute(self, dict attr_inputs):
        cdef DTYPE_t sum
        sum = 0
        cdef str src_id
        cdef DTYPE_t val
        for src_id, val in attr_inputs.items():
            sum += val
        return sum

cdef class OutputAccessor(object):

    def __init__(self, RegressionModelSimulator simulator, int idx):
        self.simulator = simulator
        self.idx = idx

    cpdef public DTYPE_t run(self):
      return self.simulator.state[self.idx]


cdef class ConstantInputAccessor(object):

    def __init__(self, DTYPE_t value):
        self.value = value

    cpdef public DTYPE_t run(self):
        return self.value


cdef class ExternalInputAccessor(object):

    def __init__(self, RegressionModelSimulator simulator, int idx):
        self.simulator = simulator
        self.idx = idx

    cpdef DTYPE_t run(self):
        return self.simulator.external_inputs[self.idx]


cdef class FeedbackInputAccessor(object):

    def __init__(self, RegressionModelSimulator simulator, int idx):
        self.simulator = simulator
        self.idx = idx

    cpdef DTYPE_t run(self):
        return self.simulator.state[self.idx]


cdef class RegressionModelSimulator(object):

    def __init__(self):
        self.input_accessors = []
        self.output_accessors = {}
        self.state = None
        self.external_inputs = None
        self._internal_inputs = None
        self._num_input_accessors = 0

    cpdef public void init(self, int num_external_inputs, int num_outputs, list input_accessors, dict output_accessors):
        self.state = np.zeros(num_outputs, dtype=DTYPE)
        self.external_inputs = np.zeros(num_external_inputs, dtype=DTYPE)
        self.input_accessors = self.input_accessors + input_accessors
        self.output_accessors = output_accessors
        self._num_input_accessors = len(self.input_accessors)
        self._internal_inputs = np.zeros(self._num_input_accessors)

        self._num_input_accessors = len(self.input_accessors)
        self._internal_inputs = np.zeros(self._num_input_accessors)

    cpdef public void step(self):
        # inputs is an ordered tuple with input values: (<P_el_set>, <SoC>)
       cdef size_t i
       for i in range(self._num_input_accessors):
           self._internal_inputs[i] = self.input_accessors[i].run()
       self.state = self.compute_responses(self._internal_inputs)


cdef class OLSModel(RegressionModelSimulator):

    def __init__(self, regression_model_description):
        """
        :param regression_model_description: OLSModelDescription
        """
        RegressionModelSimulator.__init__(self)
        self.intercept = regression_model_description.intercept
        self.coefs = regression_model_description.coefs

    cpdef public np.ndarray compute_responses(self, np.ndarray inputs):
        return self.intercept + self.coefs.dot(inputs)

    @staticmethod
    def accepts(regression_model_description):
        return type(regression_model_description) == memomodel.OLSModelDescription


class RegressionModelFactory(object):

    @staticmethod
    def create_instance(regression_model_description):
        # find all subclasses of RegressionModelSimulator
        models = RegressionModelSimulator.__subclasses__()
        # instantiate the first model, that accepts the model description
        for model in models:
            if model.accepts(regression_model_description):
                return model(regression_model_description)
        raise Exception('Error: no matching model found:', regression_model_description)

    @staticmethod
    def create_structure(RegressionModelSimulator regression_model_simulator, model_structure):
        cdef int num_external_inputs
        cdef int num_outputs
        cdef int num_virtual_states
        cdef list input_accessors
        cdef int idx
        cdef str attr
        num_external_inputs = len(model_structure.model_inputs)
        num_outputs = len(model_structure.model_outputs)
        num_virtual_states = len(model_structure.virtual_states)

        # external input: create objects that alwas return 'external_inputs'[idx]
        input_accessors = []
        for idx in range(num_external_inputs):
            input_accessors.append(ExternalInputAccessor(regression_model_simulator, idx))

        # feedback: create object, that always the value of 'current state'[idx]
        for idx in range(num_virtual_states):
            vstate = model_structure.virtual_states[idx]
            update_attr = vstate.update_attribute
            output_idx = model_structure.model_outputs.index(update_attr)
            input_accessors.append(FeedbackInputAccessor(regression_model_simulator, output_idx))

        # outputs: create objets that always return the value of output 'idx'
        output_accessors = {}
        for idx, attr in enumerate(model_structure.model_outputs):
           output_accessors[attr] = OutputAccessor(regression_model_simulator, idx)

        regression_model_simulator.init(num_external_inputs, num_outputs, input_accessors, output_accessors)

    @staticmethod
    def setup_initial_state(RegressionModelSimulator regression_model_simulator, model_structure, dict init_vals):
        cdef dict output2init
        cdef int idx
        cdef str attr_name
        output2init = {vstate.update_attribute: vstate.init_attribute for vstate in model_structure.virtual_states}
        for idx in range(len(regression_model_simulator.state)):
            attr_name = model_structure.model_outputs[idx]
            if attr_name in init_vals:
                regression_model_simulator.state[idx] = init_vals[attr_name]
            elif attr_name in output2init:
                regression_model_simulator.state[idx] = init_vals[output2init[attr_name]]
            else:
                regression_model_simulator.state[idx] = None

        # construct initial state from init vals
        # ======================================
        # The initial state must be constructed from external parameters. State variables, that do not need to be
        # initialized also have to be represented. Thats why the list of model outputs is used as basic information
        # here. Sometimes initial parameter names differ from the output name, so additionally the input- and
        # update- attributes of virtual states must be mapped accordingly.



#
# def simulate(simulator, schedule):
#     input_container = simulator.inputs
#     for p_set in schedule:
#         input_container[0] = p_set
#         simulator.step()
#
# def main():
#
#     """
#      X0     P_el_set       SoC
#     P_el   -15.4571     0.987169   34.1625
#     SoC   4.666e-05 -4.94224e-05  0.998272
#     """
#
#     input_names = ['P_el_set', 'SoC']
#     response_names = ['P_el', 'SoC']
#     A = np.array([
#         [-15.4571,     0.987169,   34.1625],
#         [4.666e-05, -4.94224e-05,  0.998272]
#     ])
#
#     ####
#     import random
#     schedule = [random.uniform(-1000, 1000) for i in range(35040)]
#     ####
#
#     #update_funcs = [ExternalInputAccessor(0), FeedbackInputAccessor(1)]
#
#     simulator = OLSModel(A)
#
#     update_funcs = [ExternalInput(simulator, 0), FeedbackInput(simulator, 1)]
#     simulator.init(2, 2, update_funcs)
#     simulator.state[0] = 0
#     simulator.state[1] = 0.5
#     simulator.inputs = np.zeros(1)
#     #import cProfile
#     #cProfile.run('simulate()', 'memosim_ext.profile')
#     simulate(simulator, schedule)
#
#
# if __name__ == '__main__':
#     main()
