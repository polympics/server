"""Command line interface for managing the server."""
import argparse
import importlib
import os
import sys
from datetime import datetime
from typing import Callable

from playhouse.migrate import PostgresqlMigrator

from .config import BASE_PATH
from .models import App, Session, db


PERMISSIONS = [
    'manage_permissions', 'manage_account_teams', 'manage_account_details',
    'manage_teams', 'authenticate_users'
]
MIGRATIONS = [
    file_name[:-3] for file_name in
    os.listdir(BASE_PATH / 'polympics_server' / 'migrations')
    if file_name.endswith('.py')
]


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
        print(e, file=sys.stderr)
        sys.exit(1)


def permission_list(raw: str) -> int:
    """Parse a permission list to a series of bit flags."""
    value = 0
    for raw_permission in raw.lower().replace('-', '_').split(','):
        try:
            value |= 1 << PERMISSIONS.index(raw_permission)
        except ValueError:
            print(f'Unknown permission "{raw_permission}".', file=sys.stderr)
            sys.exit(1)
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
        print(f'Could not find app by name or ID "{raw}".', file=sys.stderr)
        sys.exit(1)
    return app


class AppsCli:
    """CLI parser for app-related commands."""

    def __init__(self, subparsers: argparse._SubParsersAction):
        """Set up the parsers for app-related commands."""
        parser = subparsers.add_parser(
            'apps',
            description='Commands for creating, viewing and editing apps.'
        )
        subsubparsers = parser.add_subparsers(
            dest='subcommand', required=True
        )
        self.commands = {}
        for parser in (
                self.create_parser, self.edit_parser, self.delete_parser,
                self.list_parser, self.view_parser):
            parser(subsubparsers)

    def create_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the app create command."""
        self.commands['create'] = self.create
        parser = subparsers.add_parser('create', description='Create an app.')
        parser.add_argument('name', help='The name for the new app.')
        parser.add_argument(
            '-g', '--grant-permissions', type=permission_list, default=0,
            help='Permissions to grant to the new app.'
        )
        parser.add_argument(
            '-a', '--all-permissions', action='store_true',
            help='Grant all permissions to the new app.'
        )

    def create(self, args: argparse.Namespace):
        """Create an app."""
        if args.all_permissions:
            permissions = (1 << len(PERMISSIONS)) - 1
        else:
            permissions = args.grant_permissions
        app = App.create(name=args.name, permissions=permissions)
        self.show_app(app)

    def edit_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the app edit command."""
        self.commands['edit'] = self.edit
        parser = subparsers.add_parser('edit', description='Edit an app.')
        parser.add_argument(
            'app', type=app_converter,
            help='The name or ID of the app.'
        )
        parser.add_argument(
            '-t', '--reset-token', action='store_true',
            help='Reset the app\'s token.'
        )
        parser.add_argument(
            '-g', '--grant-permissions', type=permission_list, default=0,
            help='Permissions to grant to the app.'
        )
        parser.add_argument(
            '-r', '--revoke-permissions', type=permission_list, default=0,
            help='Permissions to revoke from the app.'
        )
        parser.add_argument('-n', '--name', help='A new name for the app.')

    def edit(self, args: argparse.Namespace):
        """Edit an app."""
        args.app.permissions |= args.grant_permissions
        args.app.permissions &= ~args.revoke_permissions
        if args.name:
            args.app.name = args.name
        if args.reset_token:
            args.app.reset_token()
        args.app.save()
        self.show_app(args.app)

    def delete_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the app delete command."""
        self.commands['delete'] = self.delete
        parser = subparsers.add_parser('delete', description='Delete an app.')
        parser.add_argument(
            'app', type=app_converter,
            help='The name or ID of the app.'
        )

    def delete(self, args: argparse.Namespace):
        """Delete an app."""
        args.app.delete_instance()

    def list_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the app list command."""
        self.commands['list'] = self.list_apps
        subparsers.add_parser('list', description='List all apps.')

    def list_apps(self, args: argparse.Namespace):
        """List all apps."""
        for app in App.select():
            print(f'{app.id:>2}: {app.name}')

    def view_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the app view command."""
        self.commands['view'] = self.view
        parser = subparsers.add_parser('view', description='View an app.')
        parser.add_argument(
            'app', type=app_converter,
            help='The name or ID of the app.'
        )

    def view(self, args: argparse.Namespace):
        """Command to view an app."""
        self.show_app(args.app)

    def show_app(self, app: App):
        """Show an app on stdout."""
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


class SessionsCli:
    """CLI parser for session-related commands."""

    def __init__(self, subparsers: argparse._SubParsersAction):
        """Set up the parsers for session-related commands."""
        parser = subparsers.add_parser(
            'sessions',
            description='Commands for managing user auth sessions.'
        )
        subsubparsers = parser.add_subparsers(
            dest='subcommand', required=True
        )
        self.commands = {}
        self.prune_parser(subsubparsers)

    def prune_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the session prune command."""
        self.commands['prune'] = self.prune
        subparsers.add_parser(
            'prune', description='Delete expired sessions.'
        )

    def prune(self, args: argparse.Namespace):
        """Delete all expired sessions."""
        q = Session.delete().where(Session.expires_at < datetime.now())
        count = q.execute()
        print(f'Deleted {count} expired sessions.')


class MigrationsCli:
    """CLI parser for managing database migrations."""

    def __init__(self, subparsers: argparse._SubParsersAction):
        """Set up the parsers for migration commands."""
        parser = subparsers.add_parser(
            'migrations',
            description='Commands for managing database migrations.'
        )
        subsubparsers = parser.add_subparsers(
            dest='subcommand', required=True
        )
        self.commands = {}
        for parser in (self.apply_parser, self.list_parser):
            parser(subsubparsers)

    def apply_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the migrations apply command."""
        self.commands['apply'] = self.apply
        parser = subparsers.add_parser(
            'apply', description='Apply specified migrations.'
        )
        parser.add_argument(
            'migrations', type=migration_converter, nargs='*',
            help='The migrations to apply.'
        )

    def apply(self, args: argparse.Namespace):
        """Apply specified migrations."""
        migrator = PostgresqlMigrator(db)
        for migration in args.migrations:
            print('Applying migration', migration, end='... ')
            module = importlib.import_module(
                '.migrations.' + migration, 'polympics_server'
            )
            module.apply(migrator)
            print('Done')
        print('All migrations successful.')

    def list_parser(self, subparsers: argparse._SubParsersAction):
        """Set up the parser for the migrations list command."""
        self.commands['list'] = self.list_migrations
        subparsers.add_parser(
            'list', description='List available migrations.'
        )

    def list_migrations(self, args: argparse.Namespace):
        """List available migrations."""
        print('You can specify a migration by name or ID:\n')
        for migration in MIGRATIONS:
            raw_number, *name_parts = migration.split('_')
            name = '-'.join(name_parts)
            number = raw_number.lstrip('0')
            print(f'{number:>3}: {name}')


def parse_commands(
        args: argparse.Namespace,
        commands: dict[str, dict[str, Callable]]):
    """Execute the parsed commands."""
    command = commands[args.command][args.subcommand]
    command(args)


def root_parser():
    """Parse and execute the command line args."""
    parser = argparse.ArgumentParser(
        description='Tools for managing the database and API.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    apps_cli = AppsCli(subparsers)
    sessions_cli = SessionsCli(subparsers)
    migrations_cli = MigrationsCli(subparsers)
    commands = {
        'apps': apps_cli.commands,
        'sessions': sessions_cli.commands,
        'migrations': migrations_cli.commands
    }
    parse_commands(parser.parse_args(), commands)


root_parser()
