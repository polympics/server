====================
Types of JSON object
====================

``Account``
-----------

Attributes:

- ``id`` (``string``, representing an int)
- ``name`` (``string``)
- ``discriminator`` (``string``, 4 digit Discord discriminator)
- ``avatar_url`` (optional ``string``, full URL to an avatar)
- ``team`` (optional ``Team`` object)
- ``permissions`` (``int``, see :doc:`/permissions`)
- ``created_at`` (``decimal``, seconds since the UNIX epoch)
- ``awards`` (``list`` of ``Award`` objects)

``Team``
--------

Attributes:

- ``id`` (``int``)
- ``name`` (``string``)
- ``created_at`` (``decimal``, seconds since the UNIX epoch)
- ``member_count`` (``int``)
- ``awards`` (``list`` of ``Award`` objects)

``Award``
---------

Attributes:

- ``id`` (``int``)
- ``title`` (``string``)
- ``image_url`` (``string``)

``Callback``
------------

Attributes:

- ``id`` (``int``)
- ``event`` (``string``, see :doc:`/callbacks`)
- ``url`` (``string``)

``Session``
-----------

Attributes:

- ``username`` (``string``, see :doc:`/authentication`)
- ``password`` (``string``, see :doc:`/authentication`)
- ``expires_at`` (``decimal``, seconds since the UNIX epoch)

``App``
-------

Attributes:

- ``name`` (``string``)
- ``permissions`` (``int``, see :doc:`/permissions`)
- ``username`` (``string``, see :doc:`/authentication`)
- ``password`` (``string``, see :doc:`/authentication`)

.. note::

   Not all endpoints include the ``password`` attribute when returning
   an ``App`` object for security reasons. Check endpoint-specific
   documentation.
