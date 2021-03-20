"""Command line interface for managing the server."""
from __future__ import annotations

import importlib
import os
import sys
from datetime import datetime

from playhouse.migrate import PostgresqlMigrator

from .cli_parser import Argument, CommandGroup, command, parse
from .config import BASE_PATH
from .models import Account, App, Session, db


PERMISSIONS = [
    'manage_permissions', 'manage_account_teams', 'manage_account_details',
    'manage_teams', 'authenticate_users'
]
MIGRATIONS = [
    file_name[:-3] for file_name in
    os.listdir(BASE_PATH / 'polympics_server' / 'migrations')
    if file_name.endswith('.py')
]


def error(description: str):
    """Print an error to stderr and exit."""
    print(description, file=sys.stderr)
    sys.exit(1)


def get_migration_by_id(migration_id: int) -> str:
    """Get a migration by its ID."""
    for migration in MIGRATIONS:
        check_id = migration.split('_')[0].lstrip('0')
        if check_id == str(migration_id):
            return migration
    raise ValueError(f'No migration found by ID {migration_id}.')


def get_migration_by_name(raw_name: str) -> str:
    """Get a migration by its name."""
    name = raw_name.replace('_', '-')    # Allow either.
    for migration in MIGRATIONS:
        check_name = '-'.join(migration.split('_')[1:])
        if check_name == name:
            return migration
    raise ValueError(f'No migration found by name {name}.')


def migration_converter(raw_name: str) -> str:
    """Parse a migration from the command line."""
    try:
        raw_migration_id = int(raw_name)
    except ValueError:
        raw_migration_id = None
    try:
        if raw_migration_id:
            return get_migration_by_id(raw_migration_id)
        else:
            return get_migration_by_name(raw_name)
    except ValueError as e:
        error(e)


def permission_list(raw: str) -> int:
    """Parse a permission list to a series of bit flags."""
    value = 0
    for raw_permission in raw.lower().replace('-', '_').split(','):
        try:
            value |= 1 << PERMISSIONS.index(raw_permission)
        except ValueError:
            error(f'Unknown permission "{raw_permission}".')
    return value


def app_converter(raw: str) -> App:
    """Find an app by name or ID."""
    try:
        app_id = int(raw)
    except ValueError:
        query = App.name ** raw
    else:
        query = App.id == app_id
    app = App.get_or_none(query)
    if not app:
        error(f'Could not find app by name or ID "{raw}".')
    return app


def account_converter(raw: str) -> App:
    """Find an account by ID."""
    try:
        account_id = int(raw)
    except ValueError:
        error(f'Invalid ID "{raw}": must be an int.')
    account = Account.get_or_none(Account.id == account_id)
    if not account:
        error(f'Could not find account by ID "{raw}".')
    return account


AppArgument = Argument(
    'app', type=app_converter, help='The name or ID of the app.'
)


def show_app(app: App):
    """Display an app on stdout."""
    permissions = []
    for n, permission in enumerate(PERMISSIONS):
        if app.permissions & (1 << n):
            permissions.append(permission)
    permissions = ','.join(permissions)
    print(
        f'{app.id}: {app.name}\n\n'
        f'Username: A{app.id}\n'
        f'Password: {app.token}\n'
        f'Permissions: {permissions}'
    )


class Apps(CommandGroup):
    """Commands for creating, viewing and editing apps."""

    @command(
        Argument('name', help='The name for the new app.'),
        Argument(
            '-g', '--grant-permissions', type=permission_list, default=0,
            help='Permissions to grant to the new app.'
        ),
        Argument(
            '-a', '--all-permissions', action='store_true',
            help='Grant all permissions to the new app.'
        )
    )
    def create(
            name: str, grant_permissions: int, all_permissions: bool):
        """Create an app."""
        if all_permissions:
            permissions = (1 << len(PERMISSIONS)) - 1
        else:
            permissions = grant_permissions
        app = App.create(name=name, permissions=permissions)
        show_app(app)

    @command(
        AppArgument,
        Argument(
            '-t', '--reset-token', action='store_true',
            help='Reset the app\'s token.'
        ),
        Argument(
            '-g', '--grant-permissions', type=permission_list, default=0,
            help='Permissions to grant to the app.'
        ),
        Argument(
            '-r', '--revoke-permissions', type=permission_list, default=0,
            help='Permissions to revoke from the app.'
        ),
        Argument('-n', '--name', help='A new name for the app.')
    )
    def edit(
            app: App, grant_permissions: int, revoke_permissions: int,
            name: str, reset_token: bool):
        """Edit an app."""
        app.permissions |= grant_permissions
        app.permissions &= ~revoke_permissions
        if name:
            app.name = name
        if reset_token:
            app.reset_token()
        app.save()
        show_app(app)

    @command(AppArgument)
    def delete(app: App):
        """Delete an app."""
        app.delete_instance()

    @command(name='list')
    def list_apps():
        """List all apps."""
        for app in App.select():
            print(f'{app.id:>2}: {app.name}')

    @command(AppArgument)
    def view(app: App):
        """View an app."""
        show_app(app)


class Sessions(CommandGroup):
    """Commands for managing user auth sessions."""

    @command()
    def prune():
        """Delete all expired sessions."""
        q = Session.delete().where(Session.expires_at < datetime.now())
        count = q.execute()
        print(f'Deleted {count} expired sessions.')


class Migrations(CommandGroup):
    """Commands for managing database migrations."""

    @command(Argument(
        'migrations', type=migration_converter, nargs='*',
        help='The migrations to apply.'
    ))
    def apply(migrations: list[str]):
        """Apply specified migrations."""
        migrator = PostgresqlMigrator(db)
        for migration in migrations:
            print('Applying migration', migration, end='... ')
            module = importlib.import_module(
                '.migrations.' + migration, 'polympics_server'
            )
            module.apply(migrator)
            print('Done')
        print('All migrations successful.')

    @command()
    def list_migrations():
        """List available migrations."""
        print('You can specify a migration by name or ID:\n')
        for migration in MIGRATIONS:
            raw_number, *name_parts = migration.split('_')
            name = '-'.join(name_parts)
            number = raw_number.lstrip('0')
            print(f'{number:>3}: {name}')


class Users(CommandGroup):
    """Commands for managing user accounts."""

    @command(Argument(
        'account', type=account_converter, help='The ID of the account.'
    ))
    def superuser(account: Account):
        """Grant an account every permission."""
        account.manage_permissions = True
        account.manage_account_teams = True
        account.manage_account_details = True
        account.manage_teams = True
        account.manage_own_team = True
        account.save()
        print(
            f'Made account {account.id} ({account.name}#'
            f'{account.discriminator}) a superuser.'
        )


parse()
