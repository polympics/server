"""A generic tool for parsing command line arguments into subcommands."""
from __future__ import annotations

import argparse
import dataclasses
from typing import Any, Callable, Optional


__all__ = ['Argument', 'CommandGroup', 'command', 'parse']


class Argument:
    """Class to hold data for kwargs to argparse add_argument."""

    def __init__(self, *args: str, **kwargs: Any):
        """Store the data."""
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser: argparse.ArgumentParser):
        """Add the argument to a parser."""
        parser.add_argument(*self.args, **self.kwargs)


@dataclasses.dataclass
class Command:
    """Parser for a single command."""

    callback: Callable
    args: tuple[Argument]
    description: str
    name: str

    @classmethod
    def register(
            cls, *args: Argument, description: str = '',
            name: str = None) -> Callable[[Callable], Command]:
        """Create a wrapper to register a command."""
        def wrapper(callback: Callable) -> Command:
            return cls(
                callback=callback, args=args,
                description=description or callback.__doc__,
                name=name or callback.__name__
            )
        return wrapper

    def __call__(self, args: argparse.Namespace):
        """Call the wrapped command."""
        args = args.__dict__
        del args['command']
        del args['subcommand']
        self.callback(**args)

    def add_to_parser(self, parser: argparse._SubParsersAction):
        """Add the subcommand to a parser."""
        command_parser = parser.add_parser(
            self.name, description=self.description
        )
        for argument in self.args:
            argument.add_to_parser(command_parser)


class CommandGroupMetaclass(type):
    """CLI parser for a group of related commands."""

    groups = []

    @classmethod
    def parse_and_execute(cls, **kwargs: Any):
        """Parse and execute the command the user has chosen."""
        parser = argparse.ArgumentParser(**kwargs)
        subparsers = parser.add_subparsers(dest='command', required=True)
        commands = {}
        for subcommand in cls.groups:
            subcommand(subparsers, commands)
        args = parser.parse_args()
        command = commands[args.command][args.subcommand]
        command(args)

    def __new__(
            cls, class_name: str, parents: tuple[type], attrs: dict[str, Any],
            name: Optional[str] = None,
            final: bool = True) -> CommandGroupMetaclass:
        """Create a new command group."""
        parsers = []
        for attr in attrs.values():
            if isinstance(attr, Command):
                parsers.append(attr)
        attrs['_group_parsers'] = parsers
        attrs['_group_name'] = name or class_name.lower()
        attrs['_group_description'] = attrs.get('__doc__', '')
        group_class = super().__new__(cls, class_name, parents, attrs)
        if final:
            cls.groups.append(group_class)
        return group_class


class CommandGroup(metaclass=CommandGroupMetaclass, final=False):
    """Base class for command groups."""

    def __init__(
            self, subparsers: argparse._SubParsersAction,
            commands: dict[str, CommandGroup]):
        """Add this command group to the parser."""
        this_parser = subparsers.add_parser(
            self._group_name, description=self._group_description
        )
        this_subparsers = this_parser.add_subparsers(
            dest='subcommand', required=True
        )
        this_commands = {}
        for parser in self._group_parsers:
            parser.add_to_parser(this_subparsers)
            this_commands[parser.name] = parser
        commands[self._group_name] = this_commands


command = Command.register
parse = CommandGroupMetaclass.parse_and_execute
