#!/usr/bin/env python
# encoding: utf-8
USAGE = """notifico-cli

Commands:
    server          Run the webserver.
    bootstrap       Bootstrap the database tables.

Usage:
    notifico-cli server [--host=<host>] [--port=<port>] [--debug]
    notifico-cli bootstrap

Options:
    --host=<host>           The host address to bind to.
                            [default: localhost]
    --port=<port>           The host port to bind to.
                            [default: 8084]
    --debug                 Enable debugging.
"""
import sys

from docopt import docopt

from notifico.server import create_app, db


def run_server(host, port, debug=False):
    app = create_app()
    app.run(
        host=host,
        port=port,
        debug=debug
    )


def from_cli():
    args = docopt(USAGE)

    if args['server']:
        return run_server(
            host=args['--host'],
            port=int(args['--port']),
            debug=args['--debug']
        )
    elif args['bootstrap']:
        app = create_app()

        with app.app_context():
            import notifico.models as models
            [models]
            # Create all missing database tables.
            db.create_all()


if __name__ == '__main__':
    sys.exit(from_cli())
