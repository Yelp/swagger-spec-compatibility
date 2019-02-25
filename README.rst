.. image:: https://img.shields.io/travis/com/Yelp/swagger-spec-compatibility.svg
    :target: https://travis-ci.com/Yelp/swagger-spec-compatibility?branch=master

.. image:: https://img.shields.io/codecov/c/gh/Yelp/swagger-spec-compatibility.svg
    :target: https://codecov.io/gh/Yelp/swagger-spec-compatibility

.. image:: https://img.shields.io/pypi/v/swagger-spec-compatibility.svg
    :target: https://pypi.python.org/pypi/swagger-spec-compatibility/
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/swagger-spec-compatibility.svg
    :target: https://pypi.python.org/pypi/swagger-spec-compatibility/
    :alt: Supported Python versions

swagger-spec-compatibility
==========================

About
-----


``swagger-spec-compatibility`` is a Yelp maintained library that provides tools to automatically detect
the safety of `Swagger/OpenAPI 2.0 specification <https://swagger.io/docs/specification/2-0/basic-structure/>`_ changes
with respect to **backwards compatibility**.


``swagger-spec-compatibility`` aims to give developers confidence that their spec changes are safe and that clients
built with previous versions of the Swagger spec can continue to communicate correctly.

Documentation
-------------

More documentation is available at `swagger-spec-compatibility.readthedocs.org <http://swagger-spec-compatibility.readthedocs.org/>`__.

How to Install
--------------

.. code-block:: bash

    # to install the latest released version
    $ pip install swagger-spec-compatiblity

    # to install the latest master [from Github]
    $ pip install git+https://github.com/Yelp/swagger-spec-compatibility

Example Usage
-------------
The commands below assume that the library is already installed

.. code-block:: bash

    $ swagger_spec_compatibility -h

    usage: swagger_spec_compatibility [-h]
                                  [-r {MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} [{MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} ...]]
                                  {explain,run} ...

    Tool for the identification of backward incompatible changes between two swagger specs.

    The tool provides the following level of results:
    - WARNING: the Swagger specs are technically compatible but the are likely to break known Swagger implementations
    - ERROR: new Swagger spec does introduce a breaking change respect the old implementation

    positional arguments:
      {explain,run}         help for sub-command
        explain             explain selected rules
        run                 run backward compatibility detection

    optional arguments:
      -h, --help            show this help message and exit
      -r {MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} [{MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} ...], --rules {MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} [{MIS-E001,MIS-E002,REQ-E001,REQ-E002,REQ-E003,RES-E001,RES-E002,RES-E003} ...]
                            Rules to apply for compatibility detection. (default:
                            ['MIS-E001', 'MIS-E002', 'REQ-E001', 'REQ-E002',
                            'REQ-E003', 'RES-E001', 'RES-E002', 'RES-E003'])

.. code-block:: bash

    $ swagger_spec_compatibility explain -r=REQ-E001 -r=REQ-E002 explain
    Rules explanation
    [REQ-E001] Added Required Property in Request contract:
    	Adding a required property to an object used in requests leads client request to fail if the property is not present.
    [REQ-E002] Removed Enum value from Request contract:
    	Removing an enum value from a request parameter is backward incompatible as a previously valid request will not be
    	valid. This happens because a request containing the removed enum value, valid according to the "old" Swagger spec, is
    	not valid according to the new specs.

.. code-block:: bash

    $ old_spec_path=docs/source/rules/examples/REQ-E001/old.yaml
    $ new_spec_path=docs/source/rules/examples/REQ-E001/new.yaml

    # Run with all the registered rules
    $ swagger_spec_compatibility run ${old_spec_path} ${new_spec_path}
    ERROR rules:
    	[REQ-E001] Added Required Property in Request contract : #/paths//endpoint/post/parameters/0/schema
    $ echo $?
    1

    # Run with a subset of registered rules
    $ swagger_spec_compatibility -r=MIS-E001 -r=MIS-E002 run ${old_spec_path} ${new_spec_path}
    $ echo $?
    0

Development
-----------

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`__ is
recommended to keep dependencies and libraries isolated.

Setup
~~~~~

.. code-block:: bash

    # Initialize your dev environment
    $ make minimal

    # Ensure that you have activated the virtualenvironment
    $ source ./venv/bin/activate

Tip: If you have `aactivator <https://github.com/Yelp/aactivator>`__ installed the virtual environment will
be automatically activated

How to define a new compatibility rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the following steps to define a new rule:

1. Define a new rule class in ``swagger_spec_compatibility/rules/``

.. code-block:: python

    # Example of the file content  (assume that the file will be named FILE.py)
    class RuleClassName(BaseRule):
        description = ''
        error_code = 'ERROR_CODE'
        error_level = Level.LEVEL
        rule_type = RuleType.TYPE
        short_name = ''

        @classmethod
        def validate(cls, left_spec, right_spec):
            # type: (Spec, Spec) -> typing.Iterable[ValidationMessage]
            # Implement here your logic
            raise NotImplemented()

     # Please make sure that:
     #  * `description` and `short_name` are reasonably explicative to support `swagger_spec_compatibility explain` command
     #  * `error_code` has REQ- prefix for `RuleType.REQUEST_CONTRACT`, RES- for `RuleType.RESPONSE_CONTRACT` and MIS- for `RuleType.MISCELLANEOUS`

2. Add import into ``swagger_spec_compatibllity/rules/__init__.py`` to allow rule discovery

.. code-block:: python

    from swagger_spec_compatibility.rules.FILE import RuleClassName  # noqa: F401

3. Add tests to ensure that your rule behaves as expected (tests in ``tests/rules/FILE_test.py``)

4. Add documentation for the defined rule in ``docs/source/rules/ERROR_CODE.rst``. Try to be consistent with the style
   of the others documentation pages

5. Add example of a Swagger spec change that triggers the rule in ``docs/source/rules/examples/ERROR_CODE.rst``.
   Ensure to define a `tester.py` file that will make explicit the backward incompatible change through the usage of a
   `bravado <https://github.com/Yelp/bravado>`_ client (check the other testers for examples).
   **NOTE**: The testers are executed by automated tests, this is intended to ensure that documentation is in sync with
   the codebase.


Contributing
~~~~~~~~~~~~

1. Fork it ( http://github.com/Yelp/swagger-spec-compatibility/fork )
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Add your modifications
4. Commit your changes (``git commit -m "Add some feature"``)
5. Push to the branch (``git push origin my-new-feature``)
6. Create new Pull Request

License
-------

Copyright 2019 Yelp, Inc.

Swagger Spec Compatibility is licensed with a `Apache License 2.0 <https://opensource.org/licenses/Apache-2.0>`__.
