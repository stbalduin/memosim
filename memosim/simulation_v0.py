
class SurrogateModelSimulator():
    """
    This class may be used as a surrogate for other simulation models. It has a dictionary that represents the current
    state and a set of :class:`SimulationMetaModels <MetaModelSimulator>` that may mimic the output functions
    of the original model.


    :param params: dict<str, object>,
        A dictionary mapping parameter names to constant parameter values that never change during simulations.

    :param init_vals: dict<str, object>,
        A dictionary mapping parameter names to their initial values that are needed for the first simulation
        step.

    :param metamodels: MetaModelSimulator[1..*],
        A list of transfer functions, that will be evaluated during each simulation step in order to compute new
        output values.
    """

    def __init__(self, params, init_vals, metamodels):
        """
        TODO

        :param params: dict<str, object>,
            A dictionary mapping parameter names to constant parameter values that never change during simulations.

        :param init_vals: dict<str, object>,
            A dictionary mapping parameter names to their initial values that are needed for the first simulation
            step.

        :param metamodels: MetaModelSimulator[1..*],
            A list of transfer functions, that will be evaluated during each simulation step in order to compute new
            output values.
        """
        #self.metamodels = metamodels
        self.metamodel_simulators = [MetaModelSimulator(m) for m in metamodels]

        self.state_template = self._create_template_state(init_vals, params, metamodels)

        # init state
        self.state = {}
        self.state.update(self.state_template)
        self.state.update(init_vals)  # update with values of init vars

        # previous state
        self.prev_state = None

    def _create_template_state(self, init_vals, params, transfer_functions):
        # create a template state
        template_state = {}
        # template state: names and values for params!
        template_state.update(params)
        # template state: names and None values for vars with init_vals
        for var_name, value in init_vals.items():
            template_state[var_name] = None

        # template state: names and None values for all other vars
        other_names = set()
        for m in transfer_functions:
            in_names = [name for name in m.input_names]
            out_names = [name for name in m.response_names]
            other_names = other_names.union(set(in_names))
            other_names = other_names.union(set(out_names))
        for var_name in other_names:
            if not var_name in template_state.keys():
                template_state[var_name] = None
        return template_state

    def step(self):
        new_state = {}
        new_state.update(self.state_template)

        # compute output for each metamodel
        #for m in self.metamodels:
        for m in self.metamodel_simulators:
            m_out = m.step(self.state)
            new_state.update(m_out)

        # update state
        self.prev_state = self.state
        self.state = new_state

    def __getitem__(self, attr_name):
        return self.state[attr_name]

    def __setitem__(self, attr_name, value):
        if attr_name in self.state.keys():
            self.state[attr_name] = value
        else:
            # TODO: bin mir grad nihct sicher, ob das direkt nach der
            # ERstellung des Modells nicht zu restriktiv ist
            raise ValueError('Unknown attribute: %s' % (attr_name))

    def print_state(self):
        print(self.state)

    def print_prev_state(self):
        print(self.prev_state)


class MetaModelSimulator():
    """
    This MetaModelSimulator relies on a :class:`memotrainer.metamodels.MetaModel` to compute output values.

    :param meta_model: :class:`memotrainer.metamodels.MetaModel`,
        a previously trained meta_model.

    """

    def __init__(self, metamodel):
        """

        :param meta_model: :class:`memotrainer.metamodels.MetaModel`
            a previously trained meta_model.
        """
        self.metamodel = metamodel

    def step(self, state):
        """
        Computes new values for one or more output variables.

        :param state: dict<str, object>,
            a dictionary that maps property names to values.

        :return: dict<str, object>,
            returns a dictionary that maps output names to their predicted values.

        """
        input_names = self.metamodel.input_names
        response_names = self.metamodel.response_names
        x = [state[var] for var in input_names]
        y = self.metamodel.predict([x])
        responses = {name: y[name][0] for name in response_names}
        return responses