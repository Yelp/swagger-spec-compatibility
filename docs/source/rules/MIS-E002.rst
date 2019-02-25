[MIS-E002] - Changed type
=========================

Rationale
---------
Changing the type of a field is not backward compatible as a client using "old" Swagger specs will send the field with a
different type leading the service to fail to validate the request. On the other end, if the object containing the
updated field is used in the response, it will lead to unexpected client errors when parsing the response and/or using
the updated property.

Mitigation
----------
There are no best practices for this type of issue.
The general recommended approach is: don't do it and add a new field to the spec.

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/MIS-E002/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :emphasize-lines: 14,25
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/MIS-E002/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :emphasize-lines: 14,25
   :linenos:


Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/MIS-E002/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
