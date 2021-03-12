=====================
List of API endpoints
=====================

Some endpoints which may return a large number of results use :doc:`/pagination`.
These are marked with ``[P]`` below.

See :doc:`/authentication` for details on how to authenticate when using the API.

See :doc:`/types` for the structure of objects returned by the API.

Account-related endpoints
=========================

``POST /acounts/signup``
------------------------

Parameters (JSON body):

- ``discord_id`` (``int`` or ``string`` representing int)
- ``display_name`` (``string``)
- ``discriminator`` (``int``)
- ``avatar_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of the team)
- ``permissions`` (optional ``int``, default ``0``)

Returns an ``Account`` object, or a ``409`` error if the ``discord_id`` has already been registered.

Requires the ``manage_account_details`` permission. Additionally, see :doc:`/permissions` for what permissions you are allowed to grant.

``[P] GET /accounts/search``
----------------------------

Parameters (URL query string):

- ``q`` (optional ``string``, to search for)
- ``team`` (optional ``int``, the ID of a team)

If ``team`` is passed, only returns accounts from that team.

Returns a paginated list of ``Account`` objects matching the query (see :doc:`/pagination`).

``GET /accounts/me``
--------------------

Returns the ``Account`` object associated with the session used to authenticate.

Returns a ``401`` error if an user session was not used to authenticate.

``PATCH /account/{account}``
----------------------------

Parameters (dynamic URL path):

- ``account`` (``int``, the ID of the account to get)

Parameters (JSON body):

- ``display_name`` (optional ``string``)
- ``discriminator`` (optional ``int``)
- ``avatar_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of the team to move the user to)
- ``grant_permissions`` (optional ``int``, permissions to grant the user)
- ``revoke_permissions`` (optional ``int``, permissions to revoke from the user)

Returns a ``422`` error if the account was not found (**not** a ``404`` error).

If the request was successful, returns ``204`` (no content).

Different parameters require different permissions:

====================== ===========================================
Parameter              Permission
====================== ===========================================
``display_name``       ``manage_account_details``
``discriminator``      ``manage_account_details``
``avatar_url``         ``manage_account_details``
``team``               ``manage_account_teams`` :superscript:`\*1`
``grant_permissions``  See :doc:`/permissions`
``revoke_permissions`` See :doc:`/permissions`
====================== ===========================================

:superscript:`\*1` You can also add a user to a team if you are a
member of that team and have the ``manage_own_team`` permission.

``GET /account/{account}``
--------------------------

Parameters (dynamic URL path):

- ``account`` (``int``, the ID of the account to get)

Returns an ``Account`` object if successful.

Returns a ``422`` error if the account was not found (**not** a ``404`` error).

``DELETE /account/{account}``
-----------------------------

Parameters (dynamic URL path):

- ``account`` (``int``, the ID of the account to get)

Returns ``204`` (no content) if successful.

Returns a ``422`` error if the account was not found (**not** a ``404`` error).

Requires the ``manage_account_details`` permission.

``POST /account/{account}/session``
-----------------------------------

Parameters (dynamic URL path):

- ``account`` (``int``, the ID of the account to get)

Returns a ``Session`` object, or a ``422`` error if the account was not found (**not** a ``404`` error).

Requires the ``authenticate_users`` permission, which only apps can have.

App-related endpoints
=====================

``POST /app/reset_token``
-------------------------

Reset the app token used to authenticate. Returns an ``App`` object with a token present (the new token).

Returns a ``401`` error if an app token was not used to authenticate.

``GET /app``
------------

Returns the ``App`` object (with no token present) associated with the token used to authenticate.

Returns a ``401`` error if an app token was not used to authenticate.

Team-related endpoints
======================

``POST /teams/new``
-------------------

Parameters (JSON body):

- ``name`` (``string``)

Returns a new ``Team`` object. Requires the ``manage_teams`` permission.

``[P] GET /teams/search``
-------------------------

Parameters (URL query string):

- ``q`` (optional ``string``)

Returns a paginated list of ``Team`` objects (see :doc:`/pagination`). The optional ``q`` parameter allows you to filter teams by searching in their name.

``GET /team/{team}``
--------------------

Parameters (dynamic URL path):

- ``team`` (``int``, ID of the team to get)

Returns a ``Team`` object, or a ``422`` error if not found (**not** a ``404`` error).

``PATCH /team/{team}``
----------------------

Parameters (dynamic URL path):

- ``team`` (``int``, ID of the team to edit)

Parameters (JSON body):

- ``name`` (``string``, the new name of the team)

Returns ``204`` (no content) if successful, or a ``422`` error if not found (**not** a ``404`` error).

Requires the ``manage_teams`` permission, or the ``manage_own_team`` permission and authentication with an account that is a member of the specified team.


``DELETE /team/{team}``
-----------------------

Parameters (dynamic URL path):

- ``team`` (``int``, ID of the team to delete)

Returns ``204`` (no content) if successful, or a ``422`` error if not found (**not** a ``404`` error).
