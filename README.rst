.. image:: https://github.com/Yelp/swagger-spec-compatibility/workflows/ci/badge.svg
    :target: https://github.com/Yelp/swagger-spec-compatibility/actions

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

Disclaimer
~~~~~~~~~~

| The library is not supposed to cover all the possible cases of backward incompatibility.
| This is because OpenAPI 2.0 specifications are very expressive and flexible that leads to many cases of backward incompatibility.

The detection rules currently supported are built due to the need to cover *common* breaking changes (that we've experienced internally at Yelp) or support received from contributors.

If you're experiencing breaking changes and you would have the tool help you figure it out before being late, feel free to `open issues on the project <https://github.com/Yelp/swagger-spec-compatibility/issues/new>`_.
You can also `open pull requests <#contributing>`_ implementing the rules, we're always open to contributors.

Documentation
-------------

More documentation is available at `swagger-spec-compatibility.readthedocs.org <http://swagger-spec-compatibility.readthedocs.org/>`__.

How to Install
--------------

.. code-block:: bash

    # to install the latest released version
    $ pip install swagger-spec-compatibility

    # to install the latest master [from Github]
    $ pip install git+https://github.com/Yelp/swagger-spec-compatibility

Example Usage
-------------
The commands below assume that the library is already installed

.. code-block:: bash

    $ swagger_spec_compatibility -h
    usage: swagger_spec_compatibility [-h] {explain,info,run} ...

    Tool for the identification of backward incompatible changes between two swagger specs.

    The tool provides the following level of results:
    - WARNING: the Swagger specs are technically compatible but the are likely to break known Swagger implementations
    - ERROR: new Swagger spec does introduce a breaking change respect the old implementation

    positional arguments:
      {explain,info,run}  help for sub-command
        explain           explain selected rules
        info              Reports tool's information
        run               run backward compatibility detection

    optional arguments:
      -h, --help          show this help message and exit

.. code-block:: bash

    $ swagger_spec_compatibility explain -r REQ-E001 REQ-E002
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

.. code-block:: bash

    $ swagger_spec_compatibility info
    swagger-spec-compatibility: 1.3.0
    Python version: CPython - 3.6.9
    Python compiler: GCC 4.2.1 Compatible Apple LLVM 10.0.1 (clang-1001.0.46.4)
    Discovered rules:
        MIS-E001: swagger_spec_compatibility.rules.deleted_endpoint.DeletedEndpoint
        MIS-E002: swagger_spec_compatibility.rules.changed_type.ChangedType
        REQ-E001: swagger_spec_compatibility.rules.added_required_property_in_request.AddedRequiredPropertyInRequest
        REQ-E002: swagger_spec_compatibility.rules.removed_enum_value_from_request.RemovedEnumValueFromRequest
        REQ-E003: swagger_spec_compatibility.rules.removed_properties_from_request_objects_with_additional_properties_set_to_false.RemovedPropertiesFromRequestObjectsWithAdditionalPropertiesSetToFalse
        RES-E001: swagger_spec_compatibility.rules.added_properties_in_response_objects_with_additional_properties_set_to_false.AddedPropertiesInResponseObjectsWithAdditionalPropertiesSetToFalse
        RES-E002: swagger_spec_compatibility.rules.removed_required_property_from_response.RemovedRequiredPropertyFromResponse
        RES-E003: swagger_spec_compatibility.rules.added_enum_value_in_response.AddedEnumValueInRequest

Development
-----------

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <https://virtualenv.readthedocs.io/en/latest/>`__ is
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

1. Generate the rules skeletons by running ``python -m create_new_rule``.

   The tool will be creating the detection rule class, tests, etc. Check the tool output for the exact list of created files.

2. Implement the rule logic (``swagger_spec_compatibility/rules/{filename}.py``) and ensure testing coverage (``tests/rules/{filename}_test.py``).

3. Update ``docs/source/rules/examples/{rule_code}/(new|old).yaml`` example Swagger spec change and update ``docs/source/rules/examples/{rule_code}/tester.py`` tester file.

   The objective of those files is to provide a simple spec change that triggers the backward incompatible detection rule through the usage of a bravado client (check the other testers for examples).

   **NOTE**: The testers are executed by automated tests, so ``tester.py`` should complete without errors and that the spec changes are triggering the newly created rule.

4. Add documentation for the defined rule in ``swagger_spec_compatibility/rules/{filename}.py`` and ``docs/source/rules/{error_code}.rst``.

   Try to be consistent with the style of the others documentation pages.

5. [Optional] Add integration tests to ensure that no regressions will be introduced and/or to validate edge cases of the new rule.

   Integration tests are defined as follow: ``case-<incremental number>-<number of expected reports>-reports-<short description>`` directory
   with two files: ``old.yaml`` and ``new.yaml``. The two files represent two versions of the swagger specs that need to be checked for
   backward compatibility.

Contributing
~~~~~~~~~~~~

1. Fork it (http://github.com/Yelp/swagger-spec-compatibility/fork)
2. Create your feature branch (``git checkout -b my-new-feature``)
3. Add your modifications
4. Commit your changes (``git commit -m "Add some feature"``)
5. Push to the branch (``git push origin my-new-feature``)
6. Create new Pull Request

License
-------

Copyright 2019 Yelp, Inc.

Swagger Spec Compatibility is licensed with a `Apache License 2.0 <https://opensource.org/licenses/Apache-2.0>`__.
