[REQ-E004] - Changing additionalProperties to False for a request parameter
===========================================================================

Rationale
---------
If the object is defined with additionalProperties set to False then the object will not allow presence of properties not defined on the properties section of the object definition. Changing additionalProperties from True to False makes objects sent from a client, that contain additional properties and were permitted by the "old" Swagger specs, to the server be considered invalid by the backend.

Mitigation
----------
A possible mitigation could be to not set additionalProperties to False in the object schema.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E004/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E004/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :emphasize-lines: 13
   :linenos:

Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/REQ-E004/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
