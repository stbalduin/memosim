========================
``memosim.simulation``
========================

.. automodule:: memosim.simulation


Inheritance diagram
===================

.. inheritance-diagram:: memosim.simulation
    :parts: 1


.. autoclass:: SurrogateSimulationModel
    :members:
    :show-inheritance:

.. uml::

        class SurrogateSimulationModel {
            + template_state : dict<str, obj>
            + state : dict<str, obj>
            + metamodel : MetaModelSimulator[1..*]
            + step()
        }

.. autoclass:: MetaModelSimulator
    :members:
    :show-inheritance:

.. uml::

        class MetaModelSimulator {
            + {abstract} step(state: dict<str, obj>)
        }

.. autoclass:: SimpleMetaModelSimulator
    :members:
    :show-inheritance:

.. uml::

        class SimpleMetaModelSimulator {
            + metamodel: MetaModel
            + <<create>> ApproximationSimulationModel(metamodel: MetaModel)
            + step(state: dict<str, obj>)
        }