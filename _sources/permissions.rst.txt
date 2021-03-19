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
====================== =======================================================

:superscript:`\*1` You can give users the ``manage_own_team`` permission even if you do not have the ``manage_permissions`` permission, if you have the ``manage_permissions`` and are a member of the same team as them. You cannot grant permissions you do not have.

Aswell as managing your team's metadata, and as noted above, ``manage_own_team`` allows you to remove users from your own team.
