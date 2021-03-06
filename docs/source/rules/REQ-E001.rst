[REQ-E001] - Added Required Property in Request contract
========================================================

Rationale
---------
Adding a required property to an object used in requests leads client request to fail if the property is not present.


Mitigation
----------
A possible mitigation consists of adding the property as optional with an associated default value.
In this case, the client requests don’t fail to validate and the service can assume that the property is always set.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E001/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E001/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :emphasize-lines: 16-17
   :linenos:


Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/REQ-E001/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
