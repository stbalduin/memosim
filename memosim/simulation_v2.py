import numpy as np
import memomodel

class Sum():
    def __call__(self, attr_inputs):
        sum = 0
        for src_id, val in attr_inputs.items():
            sum += val
        return sum


class OutputAccessor():
    def __init__(self, simulator, idx):
        self.simulator = simulator
        self.idx = idx

    def run(self):
        return self.simulator.state[self.idx]


class ConstantInputAccessor():
    def __init__(self, value):
        self.value = value

    def run(self):
        return self.value


class ExternalInputAccessor():
    def __init__(self, simulator, idx):
        self.simulator = simulator
        self.idx = idx

    def run(self):
        return self.simulator.external_inputs[self.idx]


class FeedbackInputAccessor():
    def __init__(self, simulator, idx):
        self.simulator = simulator
        self.idx = idx

    def run(self):
        return self.simulator.state[self.idx]


class RegressionModelSimulator():
    def __init__(self):
        self.input_accessors = []
        self.output_accessors = []
        self.state = None
        self.external_inputs = None
        self._internal_inputs = None

    def init(self, num_external_inputs, num_outputs, input_accessors, output_accessors):
        self.state = np.zeros(num_outputs)
        self.external_inputs = np.zeros(num_external_inputs)
        self.input_accessors = self.input_accessors + input_accessors
        self.output_accessors = output_accessors
        self._num_input_accessors = len(self.input_accessors)
        self._internal_inputs = np.zeros(self._num_input_accessors)

    def step(self):
        # construct all internal inputs from external inputs and from feedback from the last output
        for i in range(self._num_input_accessors):
            self._internal_inputs[i] = self.input_accessors[i].run()
        self.state = self.compute_responses(self._internal_inputs)

    def compute_responses(self, inputs):
        raise Exception('must be implemented by subclasses')

    def accepts(self, regression_model_description):
        raise Exception('must be implemented by subclasses')


class GenericModelSimulator(RegressionModelSimulator):

    def __init__(self, regression_model_description):
        self.estimator = regression_model_description.sklearn_estimator
        RegressionModelSimulator.__init__(self)


    def compute_responses(self, inputs):
        #print('inputs:', inputs)
        data = self.estimator.predict([inputs])
        #print('responses', data)
        return data[0]

    @staticmethod
    def accepts(regression_model_description):
        return True
        # auskommentiert, damit alle modelle mit dem generischen Simulator behandet werden
        #return type(regression_model_description) == memomodel.GenericModelDescription


class OLSModel(RegressionModelSimulator):
    def __init__(self, regression_model_description):
        """
        :param regression_model_description: OLSModelDescription
        """
        self.intercept = regression_model_description.intercept
        self.coefs = regression_model_description.coefs
        RegressionModelSimulator.__init__(self)

    def compute_responses(self, inputs):
        data = self.intercept + self.coefs.dot(inputs)
        return data

    @staticmethod
    def accepts(regression_model_description):
        # auskommentiert, damit alle modelle mit dem generischen Simulator behandet werden
        #return type(regression_model_description) == memomodel.OLSModelDescription
        return False

class KernelRidgeRegressionSimulator(RegressionModelSimulator):
    def __init__(self, regression_model_description):
        """
        :param regression_model_description: OLSModelDescription
        """
        #self.intercept = regression_model_description.intercept
        #self.coefs = regression_model_description.coefs
        kernel_functions = {
            'linear': KernelRidgeRegressionSimulator.linear_kernel,
            'polynomial': KernelRidgeRegressionSimulator.polynomial_kernel,
            'sigmoid': KernelRidgeRegressionSimulator.sigmoid_kernel,
            'rbf': KernelRidgeRegressionSimulator.rbf_kernel
        }
        self.kernel_function = kernel_functions[regression_model_description.kernel]
        self.gamma = regression_model_description.gamma
        self.degree = regression_model_description.degree
        self.coef0 = regression_model_description.coef0
        self.X_fit = regression_model_description.X_fit
        self.dual_coef = regression_model_description.dual_coef
        if self.gamma is None or np.isnan(self.gamma):
            self.gamma = 1.0
        RegressionModelSimulator.__init__(self)

    def compute_responses(self, inputs):
        K = self.kernel_function(inputs, self.X_fit, degree=self.degree, gamma=self.gamma, coef0=self.coef0)
        return np.dot(K, self.dual_coef)

    @staticmethod
    def linear_kernel(X, Y, degree=3, gamma=None, coef0=1):
        return np.dot(X, Y.T)

    @staticmethod
    def polynomial_kernel(X, Y, degree=3, gamma=None, coef0=1):
        # if gamma is None:
        #    gamma = 1.0 / X.shape[1]
        K = np.dot(X, Y.T)
        K *= gamma
        K += coef0
        K **= degree
        return K

    @staticmethod
    def sigmoid_kernel(X, Y, degree=3, gamma=None, coef0=1):
        #if gamma is None:
        #    gamma = 1.0 / X.shape[1]
        K = np.dot(X, Y.T)
        K *= gamma
        K += coef0
        np.tanh(K, K)  # compute tanh in-place
        return K

    @staticmethod
    def rbf_kernel(X, Y, degree=3, gamma=None, coef0=1):
        # TODO: shape of numpy arrays should be checked!
        #if gamma is None:
        #    gamma = 1.0 / X.shape[1]

        #print(Y)
        X = np.array([X])
        # row-wise squared euclidean norms of X and Y
        XX = (X * X).sum(axis=1)[:, np.newaxis]
        YY = (Y * Y).sum(axis=1)[np.newaxis, :]

        K = np.dot(X, Y.T)
        K *= -2
        K += XX
        K += YY
        np.maximum(K, 0, out=K)
        K *= -gamma
        np.exp(K, K)
        return np.reshape(K, (-1,))

    @staticmethod
    def accepts(regression_model_description):
        # auskommentiert, damit alle modelle mit dem generischen Simulator behandet werden
        #return type(regression_model_description) == memomodel.KernelRidgeRegressionModelDescription
        return False


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
    def create_structure(regression_model_simulator, model_structure):

        num_external_inputs = len(model_structure.model_inputs)
        num_outputs = len(model_structure.model_outputs)
        num_virtual_states = len(model_structure.virtual_states)

        # external input: create objects that alwas return 'external_inputs'[idx]
        input_accessors = []
        for idx in range(num_external_inputs):
            input_accessors.append(ExternalInputAccessor(regression_model_simulator, idx))

        # feedback: create object, that always retunrs the value of 'current state'[idx]
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
    def setup_initial_state(regression_model_simulator, model_structure, init_vals):

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
# def simulate():
#     input_container = simulator.external_inputs
#     for p_set in schedule:
#         input_container[0] = p_set
#         simulator.step()
#


if __name__ == '__main__':
    pass
    #
    # """
    #  X0     P_el_set       SoC
    # P_el   -15.4571     0.987169   34.1625
    # SoC   4.666e-05 -4.94224e-05  0.998272
    # """
    #
    # input_names = ['P_el_set', 'SoC']
    # response_names = ['P_el', 'SoC']
    # A = np.array([
    #     [-15.4571,     0.987169,   34.1625],
    #     [4.666e-05, -4.94224e-05,  0.998272]
    # ])
    #
    # ####
    # import random
    # schedule = [random.uniform(-1000, 1000) for i in range(35040)]
    # ####
    #
    # #update_funcs = [ExternalInputAccessor(0), FeedbackInputAccessor(1)]
    #
    # simulator = model = OLSModel(A)
    # simulator.state = (None, 0.5)
    # simulator.external_inputs = np.zeros(1)
    # simulator.input_accessors += [ExternalInputAccessor(simulator, 0), FeedbackInputAccessor(simulator, 1)]
    # simulator.finalize()
    #
    # #import cProfile
    # #cProfile.run('simulate()', 'sim_v2.profile')
    #
    # for p_set in schedule[:3]:
    #    input_container = simulator.external_inputs
    #    input_container[0] = p_set
    #    simulator.step()
    #    print(simulator.state)
