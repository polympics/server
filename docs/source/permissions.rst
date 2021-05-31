===========
Permissions
===========

Permissions are stored and transmitted as bit flags.

From least to most significant bit, the available permissions are as follows:

====================== =======================================================
Permission             Description
====================== =======================================================
manage_permissions     Manage permissions of user accounts. :superscript:`\*1`
manage_account_teams   Change the team to which users belong to.
manage_account_details Create, edit and delete accounts.
manage_teams           Create, edit and delete teams.
authenticate_users     Create authentication sessions for users (app-only).
manage_own_team        Manage the team to which you belong (user-only).
manage_awards          Create, edit and delete awards.
====================== =======================================================

:superscript:`\*1`

- You must have the ``manage_permissions`` permission edit a user's permission.
- You cannot add or remove a permission from a user if you do not have it yourself.

There are exceptions to the above relating to the ``manage_own_team`` permission, however. You can additionally add or remove it from a user if:

- You have the ``manage_own_team`` permission and are a member of the same team as them.
- You have the ``manage_permissions`` permission and the ``manage_teams`` permission.

As well as managing your team's metadata, and as noted above, ``manage_own_team`` allows you to remove users from your own team.
