=====================
List of API endpoints
=====================

Some endpoints which may return a large number of results use :doc:`/pagination`.
These are marked with ``[P]`` below.

See :doc:`/authentication` for details on how to authenticate when using the API.

See :doc:`/types` for the structure of objects returned by the API.

Account-related endpoints
=========================

``POST /acounts/new``
------------------------

Parameters (JSON body):

- ``id`` (``int`` or ``string`` representing int, a Discord ID)
- ``name`` (``string``)
- ``discriminator`` (``string``)
- ``avatar_url`` (optional ``string``)
- ``team`` (optional ``int``, the ID of the team)
- ``permissions`` (optional ``int``, default ``0``)

Returns an ``Account`` object, or a ``409`` error if the ``id`` has already been registered.

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

Contest-related endpoints
=========================

``GET /contests``
-----------------

Get a list of contests.

Returns:

- ``contests`` (an array of ``Contest`` objects)

Note that this endpoint is not paginated.

``POST /contests/new``
----------------------

Create a new contest. Requires the ``manage_contests`` permission.

Parameters (JSON body):

- ``title`` (``string``)
- ``description`` (``string``)
- ``opens_at`` (``decimal``, seconds since the UNIX epoch)
- ``closes_at`` (``decimal``, seconds since the UNIX epoch)
- ``ends_at`` (``decimal``, seconds since the UNIX epoch)

Returns the newly created ``Contest`` object.

``GET /contest/{contest}``
---------------------------

Get a contest by ID.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest to get)

Returns a ``Contest`` object or a ``422`` error if not found (**not** a ``404`` error).

``DELETE /contest/{contest}``
------------------------------

Delete a contest by ID. Requires the ``manage_contests`` permission.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest to delete)

Returns status code ``204`` (no content) or a ``422`` error if not found.

``PATCH /contest/{contest}``
-----------------------------

Update a contest by ID. Requires the ``manage_contests`` permission.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest to edit)

Parameters (JSON body):

- ``title`` (optional ``string``)
- ``description`` (optional ``string``)
- ``opens_at`` (optional ``decimal``, seconds since the UNIX epoch)
- ``closes_at`` (optional ``decimal``, seconds since the UNIX epoch)
- ``ends_at`` (optional ``decimal``, seconds since the UNIX epoch)

Returns the updated ``Contest`` object or a ``422`` error if not found (**not** a ``404`` error).

``[P] GET /contest/{contest}/submissions``
-------------------------------------------

Get a list of submissions to a contest.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Returns a paginated list of ``Submission`` objects. These will include the ``votes`` and ``author`` fields only if the contest has ended or you have the ``manage_contest_submissions`` permission.

Returns a ``422`` error if the contest is not found.

``POST /contest/{contest}/my_submission``
------------------------------------------

Make a submission to a contest. Requires an account token with the ``make_contest_submissions`` permission. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Parameters (JSON body):

- ``title`` (``string``)

Returns the newly created ``Submission`` object, without the ``votes`` or ``author`` fields.

Returns a ``422`` error if the contest is not found.

``PATCH /contest/{contest}/my_submission``
-------------------------------------------

Alter the metadata for your submission to a contest. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Parameters (JSON body):

- ``title`` (``string``)

Returns the altered ``Submission`` object, without the ``votes`` or ``author`` fields.

Returns a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest.

``GET /contest/{contest}/my_submission``
-----------------------------------------

Get your submission to a contest.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Returns the ``Submission`` object, without the ``votes`` or ``author`` fields.

Returns a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest.

``DELETE /contest/{contest}/my_submission``
--------------------------------------------

Delete your submission to a contest.  The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Returns status code ``204`` (no content) if successful, a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest.

``POST /contest/{contest}/my_submission/pieces/new``
-----------------------------------------------------

Add a piece to your submission in a contest. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)

Parameters (JSON body):

- position (optional ``int``, defaults to the end)
- caption (optional ``string``, defaults to an empty one)
- filename (optional ``string``, defaults to that of the later uploaded file)

Returns the updated ``Submission`` object if successful, a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest.

The submission object will not include the ``votes`` or ``author`` fields.

.. warning::
    The new piece will NOT be visible until you have attached a file to it (see below). You should attach a file to it immediately after sending this request.

``PUT /contest/{contest}/my_submission/piece/{position}/file``
---------------------------------------------------------------

Attach a file to a piece, or overwrite the existing file. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)
- ``position`` (``int``, the position of the piece in your submission)

The body of the request should be a file with a MIME type of ``image``, ``audio``, ``video`` or ``text`` (any subtype is acceptable).

Returns the updated ``Submission`` object if successful, a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest or no piece at the given position.

The submission object will not include the ``votes`` or ``author`` fields.

``PATCH /contest/{contest}/my_submission/piece/{position}``
------------------------------------------------------------

Edit the metadata for a piece. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)
- ``position`` (``int``, the position of the piece in your submission)

Parameters (JSON body):

- position (optional ``int``, new position for the piece)
- caption (optional ``string``)
- filename (optional ``string``)

Returns the updated ``Submission`` object if successful, a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest or no piece at the given position.

The submission object will not include the ``votes`` or ``author`` fields.

``DELETE /contest/{contest}/my_submission/piece/{position}``
-------------------------------------------------------------

Remove a piece from your submission. The contest must currently be open.

Parameters (dynamic URL path):

- ``contest`` (``int``, the ID of the contest)
- ``position`` (``int``, the position of the piece in your submission)

Returns the updated ``Submission`` object if successful, a ``422`` error if the contest is not found, or a ``404`` error if you have no submission in the contest or no piece at the given position.

The submission object will not include the ``votes`` or ``author`` fields.

``GET /submission/{submission}``
---------------------------------

Get a submission by ID.

Parameters (dynamic URL path):

- ``submission`` (``int``, the ID of the submission)

Returns a ``Submission`` object if successful, or a ``422`` error if not found.

The submission object will include the ``votes`` and ``author`` fields only if the contest has ended or you have the ``manage_contest_submissions`` permission.

``DELETE /submission/{submission}``
------------------------------------

Delete a submission by ID. Requires the ``manage_contest_submissions`` permission.

Parameters (dynamic URL path):

- ``submission`` (``int``, the ID of the submission)

Returns a status code ``204`` if successful, or a ``422`` error if not found.

``POST /submission/{submission}/vote``
---------------------------------------

Place a vote on a submission. Requires the ``vote_contest_submissions`` permission. The contest must currently be closed (but not ended).

Parameters (dynamic URL path):

- ``submission`` (``int``, the ID of the submission)

Returns a status code ``204`` if successful, or a ``422`` error if not found.

``DELETE /submission/{submission}/vote``
-----------------------------------------

Remove your vote from a submission. The contest must currently be closed (but not ended).

Parameters (dynamic URL path):

- ``submission`` (``int``, the ID of the submission)

Returns a status code ``204`` if successful, a ``404`` error if you have not voted on this submission, or a ``422`` error if not found.

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

Returns a ``Session`` object. If the token was valid but the account was not found, creates the account. Returns a ``401`` error if the token was invalid. Note that the token must be authorised for the ``identify`` scope.

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
