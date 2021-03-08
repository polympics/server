==========
Pagination
==========

When returning a potentially long list of objects, the API will use pagination.

This adds the following optional parameters to the endpoint:

- ``page`` (``int``, the page number to get, 0-indexed, default ``0``)
- ``per_page`` (``int``, the number of objects to return per-page, default ``20``)

Paginated endpoints will return an object with the following keys:

- ``page`` (``int``, matches the parameter)
- ``per_page`` (``int``, matches the parameter)
- ``pages`` (``int``, the total number of pages at the given page size)
- ``results`` (``int``, the total number of results)
- ``data`` (``array`` of objects, see endpoint-specific documentation for the type of the objects)

If a page beyond the maximum is requested, a response will be sent with ``data`` set to the empty array. An error code *will not* be used.
