[REQ-E004] - Removing properties from an object with additionalProperties set to False used as request parameter
================================================================================================================

Rationale
---------
If the object is defined with additionalProperties set to False then the object will not allow presence of properties
not defined on the properties section of the object definition. Removing a definition of an existing property makes
objects sent from a client, that is using "old" Swagger specs, to the server be considered invalid by the backend.

Mitigation
----------
A possible mitigation could be to not remove the property from the object schema, mark it as deprecated (mostly for
documentation purposes) and make sure that your business logic fills the field with a placeholder.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E004/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :emphasize-lines: 17-18
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E004/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :linenos:


Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/REQ-E004/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
