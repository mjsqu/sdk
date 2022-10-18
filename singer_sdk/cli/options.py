"""Helpers for building the CLI for a Singer tap or target."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import click


class NestedOption(click.Option):
    """A Click option that has suboptions."""

    def __init__(
        self,
        *args: Any,
        suboptions: Sequence[click.Option] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the option.

        Args:
            *args: Positional arguments to pass to the parent class.
            suboptions: A list of suboptions to be added to the context.
            **kwargs: Keyword arguments to pass to the parent class.
        """
        self.suboptions = suboptions or []
        super().__init__(*args, **kwargs)

    def handle_parse_result(
        self,
        ctx: click.Context,
        opts: Mapping[str, Any],
        args: list[Any],
    ) -> tuple[Any, list[str]]:
        """Handle the parse result.

        Args:
            ctx: The Click context.
            opts: The options.
            args: The arguments.

        Raises:
            UsageError: If an option is used without the parent option.

        Returns:
            The parse result.
        """
        ctx.ensure_object(dict)
        ctx.obj[self.name] = {}

        if self.name in opts:
            for option in self.suboptions:
                if option.name:
                    value = opts.get(option.name, option.get_default(ctx))
                    ctx.obj[self.name][option.name] = value
        else:
            for option in self.suboptions:
                if option.name in opts:
                    errmsg = f"{option.opts[0]} is not allowed without {self.opts[0]}"
                    raise click.UsageError(errmsg)

        return super().handle_parse_result(ctx, opts, args)

    def as_params(self) -> list[click.Option]:
        """Return a list of options, including this one and its suboptions.

        Returns:
            List of options.
        """
        return [self, *self.suboptions]
