[REQ-E002] - Removed Enum value from Request contract
=====================================================

Rationale
---------
Removing an enum value from a request parameter is backward incompatible as a previously valid request will not be valid.
This happens because a request containing the removed enum value, valid according to the "old" Swagger spec, is not valid
according to the new specs.

Mitigation
----------
There are no best practices for this type of issue.
The general recommendation would be to avoid as much as possible this type of change.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E002/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :emphasize-lines: 18
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/REQ-E002/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :linenos:


Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/REQ-E002/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
