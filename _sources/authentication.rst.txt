==============
Authentication
==============

This API uses HTTP basic authentication. You don't have to provide any authentication, but you will only be able to access read-only endpoints.

There are two types of credentials: app credentials and user session credentials. The username for an app will start with ``A``, the username will start with ``S``.

App Credentials
---------------

The only way to create an app is by using the server management CLI. You create one with the following command:

.. code:: bash

   $ python3 -m polympics_server apps create <name>

You can get the credentials for an existing app with:

.. code:: bash

   $ python3 -m polympics_server apps view <name_or_id>

Use ``--help`` for more information.

User Session Credentials
------------------------

You can get user session credentials from the ``/account/{account}/session`` endpoint (see :doc:`endpoints`).
