Welcome to Swagger Spec Compatibility's documentation!
======================================================

``swagger-spec-compatibility`` is a Yelp maintained library that provides tools to automatically detect
the safety of `Swagger/OpenAPI 2.0 specification <https://swagger.io/docs/specification/2-0/basic-structure/>`_ changes
with respect to **backwards compatibility**.


``swagger-spec-compatibility`` aims to give developers confidence that their spec changes are safe and that clients
built with previous versions of the Swagger spec can continue to communicate correctly.

Disclaimer
~~~~~~~~~~

| The library is not supposed to cover all the possible cases of backward incompatibility.
| This is because OpenAPI 2.0 specifications are very expressive and flexible that leads to many cases of backward incompatibility.

The detection rules currently supported are built due to the need to cover *common* breaking changes (that we've experienced internally at Yelp) or support received from contributors.

If you're experiencing breaking changes and you would have the tool help you figure it out before being late, feel free to `open issues on the project <https://github.com/Yelp/swagger-spec-compatibility/issues/new>`_.
You can also `open pull requests <#contributing>`_ implementing the rules, we're always open to contributors.


.. toctree::
   :maxdepth: 2
   :caption: Content:

   rules/index
   modules
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
