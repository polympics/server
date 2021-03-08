====================
Types of JSON object
====================

``Account``
-----------

Attributes:

- ``discord_id`` (``int``)
- ``display_name`` (``string``)
- ``team`` (``Team`` object)
- ``permissions`` (``int``, see :doc:`/permissions`)
- ``created_at`` (``decimal``, seconds since the UNIX epoch)

``Team``
--------

Attributes:

- ``id`` (``int``)
- ``name`` (``string``)
- ``created_at`` (``decimal``, seconds since the UNIX epoch)
- ``member_count`` (``int``)

``Session``
-----------

Attributes:

- ``username`` (``string``, see :doc:`/authentication`)
- ``password`` (``string``, see :doc:`/authentication`)
- ``expires_at`` (``decimal``, seconds since the UNIX epoch)

``App``
-------

Attributes:

- ``display_name`` (``string``)
- ``permissions`` (``int``, see :doc:`/permissions`)
- ``username`` (``string``, see :doc:`/authentication`)
- ``password`` (``string``, see :doc:`/authentication`)

.. note::

   Not all endpoints include the ``password`` attribute when returning
   an ``App`` object for security reasons. Check endpoint-specific
   documentation.