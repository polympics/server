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

``Contest``
-----------

Attributes:

- ``id`` (``int``)
- ``title`` (``string``)
- ``description`` (``string``)
- ``opens_at`` (``decimal``, seconds since the UNIX epoch)
- ``closes_at`` (``decimal``, seconds since the UNIX epoch)
- ``ends_at`` (``decimal``, seconds since the UNIX epoch)
- ``state`` (``string``, one of ``"unopened"``, ``"open"``, ``"closed"`` or ``"ended"``)

``Submissions``
---------------

Attributes:

- ``id`` (``int``)
- ``title`` (``string``)
- ``pieces`` (``list`` of ``Piece`` objects)
- ``author`` (``Account`` object)
- ``votes`` (``int``)

.. note::
   Only pieces with an attached file will be included.

   The ``author`` and ``votes`` fields will only be present if the contest is over or you have the ``manage_contest_submissions`` permission.

``Piece``
---------

Attributes:

- ``position`` (``int``)
- ``caption`` (``string``)
- ``mime_type`` (``string``)
- ``filename`` (``string``)
- ``url`` (``string``, path relative to the API root where the file can be accessed)

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
