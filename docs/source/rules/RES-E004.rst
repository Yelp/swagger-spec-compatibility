[RES-E004] - TODO
=====================================================

Rationale
---------
TODO

Mitigation
----------
TODO

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/RES-E004/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/RES-E004/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :linenos:
   :emphasize-lines: 16

Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/RES-E004/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
