Changelog
=========

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
