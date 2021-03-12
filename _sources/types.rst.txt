====================
Types of JSON object
====================

``Account``
-----------

Attributes:

- ``discord_id`` (``string``, representing an int)
- ``display_name`` (``string``)
- ``discriminator`` (``int``, 4 digit Discord discriminator)
- ``avatar_url`` (optional ``string``, full URL to an avatar)
- ``team`` (optional ``Team`` object)
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
