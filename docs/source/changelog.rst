Changelog
=========

1.2.3 (2020-10-26)
------------------
* Fix an issue with REQ-E004 erroring with false positives (`PR #36 <https://github.com/Yelp/swagger-spec-compatibility/pull/36>`_)

1.2.3 (2020-10-26)
------------------
* Improve performance when walking very large Swagger specs (`PR #34 <https://github.com/Yelp/swagger-spec-compatibility/pull/34>`_)

1.2.2 (2020-10-20)
------------------
* Fix an issue comparing Swagger specs containing circular references  (`PR #33 <https://github.com/Yelp/swagger-spec-compatibility/pull/33>`_)

1.2.1 (2020-01-07)
------------------
* Blacklist ``bravado-core==5.16.0`` as not compatible with the library (`PR #18 <https://github.com/Yelp/swagger-spec-compatibility/pull/18>`_)

1.2.0 (2019-03-27)
------------------
* Expose read-the-docs documentation links for rules defined by the library (`PR #9 <https://github.com/Yelp/swagger-spec-compatibility/pull/9>`_)

1.1.0 (2019-03-07)
------------------
* Add ``--blacklist-rules`` CLI option to ignore certain rules during the checks (`PR #6 <https://github.com/Yelp/swagger-spec-compatibility/pull/6>`_)
* Fixed ``SchemaWalker`` to properly combine old and new parameters during the spec traversal. (`PR #7 <https://github.com/Yelp/swagger-spec-compatibility/pull/7>`_)
* Simplified creation and registration of new rules (`PR #8 <https://github.com/Yelp/swagger-spec-compatibility/pull/8>`_)

1.0.1 (2019-02-26)
------------------
* Updated package metadata

1.0.0 (2019-02-26)
------------------
* Initial library implementation with definition of the following rules:

  - `[REQ-E001] <rules/REQ-E001.html>`_ - Added Required Property in Request contract
  - `[REQ-E002] <rules/REQ-E002.html>`_ - Removed Enum value from Request contract
  - `[REQ-E003] <rules/REQ-E003.html>`_ - Removing properties from an object with additionalProperties set to False used as request parameter
  - `[RES-E001] <rules/RES-E001.html>`_ - Added properties in an object with additionalProperties set to False used in response
  - `[RES-E002] <rules/RES-E002.html>`_ - Remove a required property from an object used in responses
  - `[RES-E003] <rules/RES-E003.html>`_ - Added Enum value in Response contract
  - `[MIS-E001] <rules/MIS-E001.html>`_ - Delete an endpoint
  - `[MIS-E002] <rules/MIS-E002.html>`_ - Changed type
