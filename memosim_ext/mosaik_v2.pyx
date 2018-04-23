import mosaik_api

import h5db
import memomodel

cimport numpy as np
import numpy as np
cimport cython

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


cimport memosim_ext.simulation_v2 as sim
import memosim_ext.simulation_v2 as sim

def load_model_description(surrogate_model_file, surrogate_name):
    """
    TODO: evtl. einbauen, dass nach surrogatnamen gefiltert wird. Dann könnten mehrere modelle in einer Datei gelagert
    werden, aber sie müssten noch um einen namen erweitert werden.
    """
    db = memomodel.MeMoSimDB(surrogate_model_file)
    db.open(access_mode=h5db.H5AccessMode.READ_EXISTING_FILE)
    model_description = db.load_objects(memomodel.SimulationModelDescription)
    db.close()
    return model_description[0]

def create_simulator_meta_data(model_structure, model_name):
    param_names = model_structure.model_parameters
    attr_names = model_structure.model_outputs + model_structure.model_inputs
    meta = {}
    meta['models'] = {
        model_name: {
            'public': True,
            'params': param_names,  # parameters for model creation
            'attrs': attr_names  # attributes available within
        }
    }
    return meta


class EIDGenerator(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.index = -1

    def next(self):
        self.index += 1
        return '%s%d' % (self.prefix, self.index)


class MosaikMeMoSimulator(mosaik_api.Simulator):

    SIM_CONFIG = {'python': 'memosim_ext.mosaik_v2:MosaikMeMoSimulator'}

    def __init__(self):
        super().__init__({})
        # TODO: prefix  mit original model angleichen?
        self.eid_generator = EIDGenerator('memo_')
        self.model_instances = {}  # maps EIDs to model
        self.sid = None
        self.step_size = None  # step size of the simulation

    def init(self, sid, step_size, surrogate_model_file, surrogate_name):
        self.sid = sid
        self.step_size = step_size
        self.model_name = surrogate_name

        # load information about the metamodel from the model file
        model_description = load_model_description(surrogate_model_file, surrogate_name)
        self.model_structure = model_description.model_structure
        self.regression_model = model_description.regression_model

        # create meta data dynamically:
        self.meta.update(create_simulator_meta_data(self.model_structure, surrogate_name))

        # prepare DEFAULt aggregation functions for inputs
        self.aggregators = [sim.Sum() for attr in self.model_structure.model_inputs]

        return self.meta

    def create(self, num, model, **init_vals):
        entities = []
        for i in range(num):
            eid = self.eid_generator.next()

            # create the simulator
            simulator = sim.RegressionModelFactory.create_instance(self.regression_model)
            sim.RegressionModelFactory.create_structure(simulator, self.model_structure)

            # initialize the simulator
            sim.RegressionModelFactory.setup_initial_state(simulator, self.model_structure, init_vals)

            self.model_instances[eid] = simulator

            entities.append({'eid': eid, 'type': model})
        return entities

    def step(self, time, inputs):
        #cdef long time
        #cdef dict inputs
        """
        see :meth:`mosaik_api.Simulator.step()`

        :param time: int
            seconds since simulation start.

        :param inputs:  a dict of dicts mapping entity IDs to attributes and dicts of values
            (each simulator has do decide on its own how to reduce the values (e.g., as its sum, average or maximum).
            This simulator ignores inputs.

        :return: int
            time of the next simulation step (also in seconds since simulation start)
        """
        cdef str eid
        cdef dict attrs
        cdef sim.RegressionModelSimulator simulator
        cdef np.ndarray input_container
        cdef int i
        cdef str input_name
        for eid, attrs in inputs.items():
            simulator = self.model_instances[eid]
            input_container = simulator.external_inputs
            for i, input_name in enumerate(self.model_structure.model_inputs):
                input_container[i] = self.aggregators[i].compute(attrs[input_name])
            simulator.step()
        return (time + self.step_size)


    def get_data(self, outputs):
        """
        see :meth:`mosaik_api.Simulator.get_data()`

        :param outputs: outputs is a dict mapping entity IDs to lists of attribute names whose values are requested.

        :return: The return value needs to be a dict of dicts mapping entity IDs and attribute names to their values.
        """
        cdef dict data
        cdef str eid
        cdef list attrs
        cdef str attr

        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                data[eid][attr] = self.model_instances[eid].output_accessors[attr].run()
        return data
