[MIS-E001] - Delete an endpoint
===============================

Rationale
---------
A Swagger service should be only serve endpoints defined via Swagger specs.
Once an endpoint is removed from the Swagger specs this implies that the endpoint is not served anymore and any call
to it will fail (as there is no implementation for it; HTTP/400, HTTP/404 or HTTP/500 could be expected in this case).

Mitigation
----------
There are no general approaches to make this change without risks.
The main recommendations are:
ensure that the endpoint is marked as deprecated and notify all the clients about the endpoint removal timeline
ensure that the endpoint is not called anymore.

*Note*: this is not always possible, think about the case of public APIs used by mobile devices.
In such case validate with the clients product owners that is possible to returns errors.

*PS*: be aware that the fact that an endpoint is not called anymore does not implies that it won't be called in the
future (maybe the obsolete client is just not used at the moment)

Example
-------
Old Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/MIS-E001/old.yaml
   :name: Old Swagger Spec
   :language: yaml
   :emphasize-lines: 11-14
   :linenos:

New Swagger Specs
~~~~~~~~~~~~~~~~~

.. literalinclude:: examples/MIS-E001/new.yaml
   :name: New Swagger Spec
   :language: yaml
   :linenos:

Backward Incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~
The following snippet triggers the incompatibility error.

.. literalinclude:: examples/MIS-E001/tester.py
   :language: py
   :linenos:

**NOTE**: The code is taking advantage of `bravado <https://github.com/Yelp/bravado>`_
