=========
Callbacks
=========

Callbacks allow apps to register HTTP endpoints that will be sent a request when an event occurs. To register a callback, use ``PUT /callbacks/{event}`` (see :doc:`/endpoints` for more information).

Callback requests sent to reigstered URLs will be ``POST`` requests. The body will be a JSON object (different depending on the type of event). An ``Authorization`` header will be sent using the ``Bearer`` authorisation scheme and the token set to the secret provided when creating the callback.

For example, if a callback is registered like so:

.. code-block:: text

   PUT /callbacks/account_team_update
   Authorization: Basic QTE6aHR0cHM6Ly95b3V0dWJlLmNvbS93YXRjaD92PWRRdzR3OVdnWGNR

   {
       "url": "https://example.com/cbs/team_changed",
       "secret": "obviously-dont-use-this"
   }

Then when an event is triggered, it will look like this:

.. code-block:: text

   POST https://example.com/cbs/team_changed
   Authorization: Bearer obviously-dont-use-this

   {
       ...
   }

The following event types are currently defined:

``account_team_update``
=======================

Called when a user's team is changed. Data sent is an object with the following keys:

- ``account`` (the new ``Account`` object)
- ``team`` (the new ``Team`` object, or ``null`` if the user no longer has a team)
