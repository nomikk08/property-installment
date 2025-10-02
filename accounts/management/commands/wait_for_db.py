from __future__ import annotations

import datetime
import socket
import subprocess
import time

from django.core.management import BaseCommand, CommandError
from django.db import connection
import os

class Command(BaseCommand):
    help = "Test if default database is available."
    requires_migrations_checks = False

    # requires_system_checks = False

    def add_arguments(self, parser):
        # optional timeout parameter
        parser.add_argument(
            "-t",
            "--timeout",
            dest="timeout",
            default=15,
            help="Timeout in seconds.",
        )
        parser.add_argument(
            "--cmd",
            dest="sub_cmd",
            nargs="*",
            help="Execute command with args after the test finishes",
        )

    def handle(self, *args, **options):
        conn_params = connection.get_connection_params()
        db_found = interrupted = False
        start = datetime.datetime.now()
        timeout = options["timeout"]
        timeout_td = datetime.timedelta(seconds=timeout)
        timeout_dt = start + timeout_td

        self.stdout.write(
            "wait-for-db: waiting {} seconds for {}:{}".format(timeout, conn_params["host"], conn_params["port"])
        )

        while datetime.datetime.now() < timeout_dt:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    conn_err = sock.connect_ex((conn_params["host"], int(conn_params["port"])))
                except OSError as exc:
                    raise CommandError(
                        "wait-for-db: Error connecting to '{}:{}': {}".format(
                            conn_params["host"], conn_params["port"], exc
                        )
                    )
                if conn_err == 0:
                    sock.close()
                    db_found = True
                    break
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                interrupted = True
                if sock:
                    sock.close()

        if db_found:
            self.stdout.write(
                self.style.SUCCESS(
                    "wait-for-db: {}:{} is available after {} seconds".format(
                        conn_params["host"],
                        conn_params["port"],
                        (datetime.datetime.now() - start).total_seconds(),
                    )
                )
            )
        elif interrupted:
            raise CommandError(
                "wait-for-db: waiting for {}:{} interrupted after {} seconds".format(
                    conn_params["host"],
                    conn_params["port"],
                    (datetime.datetime.now() - start).total_seconds(),
                )
            )
        else:
            raise CommandError(
                "wait-for-db: timeout occurred after waiting {} seconds for {}:{}".format(
                    timeout, conn_params["host"], conn_params["port"]
                )
            )
        if options["sub_cmd"]:
            self.stdout.write(self.style.SUCCESS("wait-for-db: exec {}".format(" ".join(options["sub_cmd"]))))
            try:
                cmd_to_execute = [command for command in options["sub_cmd"][0].split(" ")]
                subprocess.check_call(cmd_to_execute)
            except (OSError, subprocess.CalledProcessError) as exc:
                raise CommandError("wait-for-db: {}".format(exc))
            except KeyboardInterrupt:
                pass
