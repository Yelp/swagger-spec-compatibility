[RES-E001] - Added properties in an object with additionalProperties set to False used in response
==================================================================================================

Rationale
---------
If the object is defined with additionalProperties set to False then the object will not allow presence of properties not
defined on the properties section of the object definition.
Adding a definition of a new property makes object sent from the server to the client be considered invalid by a client
that is using "old" Swagger specs.

Mitigation
----------
A general suggestion would be to avoid setting additionalProperties to False for request objects as this prevents
backward compatible safe object modifications. A possible mitigation to this requires the implementation of a new
endpoint that returns the new object schema.

**NOTE**: Implementing a new endpoint is usually cheap but comes with the complexity of handling multiple versions of similar endpoints.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/RES-E001/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/RES-E001/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :emphasize-lines: 17-18
   :linenos:


Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/RES-E001/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
