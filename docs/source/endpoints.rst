=====================
List of API endpoints
=====================

Some endpoints which may return a large number of results use :doc:`/pagination`.
These are marked with ``[P]`` below.

See :doc:`/authentication` for details on how to authenticate when using the API.

See :doc:`/types` for the structure of objects returned by the API.

Account-related endpoints
=========================

``GET /accounts/signups``
-------------------------

Check if signups are open.

Returns a JSON object containing:

- ``signups_open`` (``boolean``)

``POST /acounts/new``
---------------------

Parameters (JSON body):

- ``id`` (``int`` or ``string`` representing int, a Discord ID)
- ``name`` (``string``)
- ``discriminator`` (``string``)
- ``avatar_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of the team)
- ``permissions`` (optional ``int``, default ``0``)

Returns an ``Account`` object, a ``409`` error if the ``id`` has already been registered, or a ``403`` error if signups are closed.

Requires the ``manage_account_details`` permission. Additionally, see :doc:`/permissions` for what permissions you are allowed to grant.

``[P] GET /accounts/search``
----------------------------

Parameters (URL query string):

- ``q`` (optional ``string``, to search for)
- ``team`` (optional ``int``, the ID of a team)

If ``team`` is passed, only returns accounts from that team.

Returns a paginated list of ``Account`` objects matching the query (see :doc:`/pagination`).

``PATCH /account/{account}``
----------------------------

Parameters (dynamic URL path):

- ``account`` (``int``, the ID of the account to get)

Parameters (JSON body):

- ``name`` (optional ``string``)
- ``discriminator`` (optional ``string``)
- ``avatar_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of the team to move the user to)
- ``grant_permissions`` (optional ``int``, permissions to grant the user)
- ``revoke_permissions`` (optional ``int``, permissions to revoke from the user)
- ``discord_token`` (optional ``string``, Discord token to fetch user data from)

Note that ``team`` can also be ``0``, which indicates that the user should be
removed from their team.

Returns a ``422`` error if the account was not found (**not** a ``404`` error).

If ``discord_token`` was passed but was invalid or didn't have the ``indentify`` scope, a ``422`` error is returned. If the token was valid but was for the wrong account ID, a ``403`` error is returned.

Returns an ``Account`` object if successful.

Different parameters require different permissions:

====================== ===========================================
Parameter              Permission
====================== ===========================================
``name``               ``manage_account_details``
``discriminator``      ``manage_account_details``
``avatar_url``         ``manage_account_details``
``team``               ``manage_account_teams`` :superscript:`\*1`
``grant_permissions``  See :doc:`/permissions`
``revoke_permissions`` See :doc:`/permissions`
``discord_token``      None
====================== ===========================================

:superscript:`\*1` You can also remove a user from a team if you are a
member of that team and have the ``manage_own_team`` permission. You can
also add yourself to a team.

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

Requires the ``manage_account_details`` permission, or being authenticated for this account.

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

Returns a ``Team`` object if successful, or a ``422`` error if not found (**not** a ``404`` error).

Requires the ``manage_teams`` permission, or the ``manage_own_team`` permission and authentication with an account that is a member of the specified team.


``DELETE /team/{team}``
-----------------------

Parameters (dynamic URL path):

- ``team`` (``int``, ID of the team to delete)

Returns ``204`` (no content) if successful, or a ``422`` error if not found (**not** a ``404`` error).

Award-related endpoints
=======================

``POST /awards/new``
--------------------

Creates a new award. An award is given to a selection of users but also to their team. Requires the ``manage_awards`` permission.

Parameters (JSON body):

- ``title`` (``string``)
- ``image_url`` (``string``)
- ``team`` (``int``, the ID of a team)
- ``accounts`` (``list`` of ``string`` s, the IDs of accounts)

``team`` *should* (but is not required to) refer to a team that all the ``accounts`` are part of.

Returns an ``Award`` object.

``PATCH /award/{award}``
-------------------------

Updates an existing award. Requires the ``manage_awards`` permission.

Parameters (dynamic URL path):

- ``award`` (``int``, the ID of the award to edit)

Parameters (JSON body):

- ``title`` (optional ``string``)
- ``image_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of a team)

Returns an ``Award`` object, or a ``422`` error if not found (**not** a ``404`` error).

``GET /award/{award}``
-----------------------

Get the details of an award.

Parameters (dynamic URL path):

- ``award`` (``int``, the ID of the award to get)

Returns:

- ``award (an ``Award`` object)
- ``awardees`` (a ``list`` of ``Account`` objects)
- ``team`` (optional ``Team`` object)

Instead returns a ``422`` error if not found (**not** a ``404`` error).

``DELETE /award/{award}``
--------------------------

Remove an award. Requires the ``manage_awards`` permission.

Parameters (dynamic URL path):

- ``award`` (``int``, the ID of the award to delete)

Returns ``204`` (no content) if successful, or a ``422`` error if not found (**not** a ``404`` error).

``PUT /account/{account}/award/{award}``
----------------------------------------

Give an existing award to a new user. Requires the ``manage_awards`` permission.

Parameters (dynamic URL path):

- ``account`` (``string``, the ID of the account to assign the award to)
- ``award`` (``int``, the ID of the award to assign)

Returns ``201`` with no content if successful, ``208`` if the user already had the award, or ``422`` if the user or award was not found.

``DELETE /account/{account}/award/{award}``
-------------------------------------------

Remove an award from a user. Requires the ``manage_awards`` permission.

Parameters (dynamic URL path):

- ``account`` (``string``, the ID of the account to remove the award from)
- ``award`` (``int``, the ID of the award to remove)

Returns ``204`` (no content) if successful, ``404`` if the user did not have the award, or ``422`` if the user or award was not found.

Callback-related endpoints
==========================

``PUT /callback/{event}``
-------------------------

Create a callback for a specified event type. Requires an app token.

Parameters (dynamic URL path):

- ``event`` (``string``, see :doc:`/callbacks` for event types)

Parameters (JSON body):

- ``url`` (``string``, the URL to recieve events)
- ``secret`` (``string``, a secret to use when sending events)

Returns a ``Callback`` object. If a callback already exists for this event type, this endpoint will override it. If the event type is invalid, returns a ``422`` error.

``DELETE /callback/{event}``
----------------------------

Delete the callback for a specified event type. Requires an app token.

Parameters (dynamic URL path):

- ``event`` (``string``, the event type to delete the callback for)

Returns ``204`` (no content) if successful, a ``422`` error if the event type is invalid, or ``404`` error if there is no callback registered for the event type.

``GET /callback/{event}``
-------------------------

Get details on a registered callback. Requires an app token.

Parameters (dynamic URL path):

- ``event`` (``string``, see :doc:`/callbacks` for event types)

Returns a ``Callback`` object if successful, a ``422`` error if the event type is invalid, or ``404`` error if there is no callback registered for the event type.

``GET /callbacks``
------------------

Get all registered callbacks for the authenticated app. Requires an app token.

Returns:

- ``callbacks`` (an object where the keys are event types and the values are the registered callback URLs)

Authentication-related endpoints
================================

``POST /auth/discord``
----------------------

Creates a session from a Discord user token (obtainable with Discord OAuth2).

Parameters (JSON body):

- ``token`` (``string``, the Discord token)

Returns a ``Session`` object. If the token was valid but the account was not found, creates the account, or returns a ``403`` error if signups are closed. Returns a ``401`` error if the token was invalid Note that the token must be authorised for the ``identify`` scope.

``POST /auth/create_session``
-----------------------------------

Parameters (JSON body):

- ``account`` (``int``, the ID of the account to get)

Returns a ``Session`` object, or a ``422`` error if the account was not found (**not** a ``404`` error).

Requires the ``authenticate_users`` permission, which only apps can have.

``POST /auth/reset_token``
--------------------------

Reset the token used to authenticate. Returns an ``App`` object with a token present if an app token was used to authenticate, or a ``Session`` object if a user token was used to authenticate.

Returns a ``401`` error if no authentication was used.

``GET /auth/me``
----------------

Returns either an ``App`` object (with no token present) or an ``Account`` object, depending on what token was used to authenticate.

Returns a ``401`` error if no authentication was used.
