"""Management command base classes."""
import json
import logging
import time
from collections import Counter

import kombu.exceptions
from celery.result import AsyncResult, ResultSet
from django.conf import settings
from django.core.management.base import BaseCommand

from failmap.app.common import ResultEncoder
from failmap.celery import app

log = logging.getLogger(__name__)


class TaskCommand(BaseCommand):
    """A command that performs it's intended behaviour through a Celery task.

    The task can be run directly, sync- and asynchronously.

    Direct execution will run the task as if it was a direct function call.

    Sync execution will use the Celery framework to execute the task on
    a (remote) worker destined to execute tasks of this type. It will wait for
    execution to complete and return the task result/logging.

    Async is like Synchronous execution but it will not wait for it to complete.
    No result or logging will be returned.

    Direct and sync methods allow the task to be interupted during execution
    using ctrl-c.

    Sync and async methods require connection to a message broker, direct does not.
    """

    task = None
    # it is a anti-pattern to instantiate empty lists/dicts as class parameters
    # but since management commands are contained in their own invocation this can fly
    args = list()
    kwargs = dict()

    def _add_arguments(self, parser):
        """Method to allow subclasses to add command specific arguments."""

    def add_arguments(self, parser):
        """Add common argument for Celery tasks."""
        self.mutual_group = parser.add_mutually_exclusive_group()

        parser.add_argument('-m', '--method', default='direct',
                            choices=['direct', 'sync', 'async'],
                            help='Execute the task directly or on remote workers.')

        parser.add_argument('-i', '--interval', default=5, type=int,
                            help="Interval between status reports (sync only).")

        self.mutual_group.add_argument('-t', '--task_id', default='',
                                       help="Report status for task ID and return result (if available).")

        self._add_arguments(parser)

    def compose(self, *args, **options):
        """Placeholder to allow subclass to compose a task(set) if task is not specified."""
        raise NotImplementedError()

    def handle(self, *args, **options):
        """Command handle logic, eg: logging."""
        # set django loglevel based on `-v` argument
        verbosity = int(options['verbosity'])
        root_logger = logging.getLogger('')
        if verbosity == 2:
            root_logger.setLevel(logging.DEBUG)
        elif verbosity == 1:
            root_logger.setLevel(logging.INFO)
        elif verbosity == 0:
            root_logger.setLevel(logging.ERROR)

        self.interval = options['interval']

        if options['task_id']:
            result = self.wait_for_result(ResultSet([AsyncResult(options['task_id'])]))
        else:
            result = self.run_task(*args, **options)

        return json.dumps(result, cls=ResultEncoder)

    def run_task(self, *args, **options):
        # try to compose task if not specified
        if not self.task:
            self.task = self.compose(*args, **options)

        # execute task based on selected method
        if options['method'] in ['sync', 'async']:
            # verify if broker is accessible (eg: might not be started in dev. environment)
            try:
                app.connection().ensure_connection(max_retries=3)
            except kombu.exceptions.OperationalError:
                log.warning(
                    'Connection with task broker %s unavailable, tasks might not be starting.',
                    settings.CELERY_BROKER_URL)

            task_id = self.task.apply_async(args=self.args, kwargs=self.kwargs)
            log.info('Task scheduled for execution.')
            log.debug("Task ID: %s", task_id.id)

            # wrap a single task in a resultset to not have 2 ways to handle results
            if not isinstance(task_id, ResultSet):
                task_id = ResultSet([task_id])

            if options['method'] == 'sync':
                return self.wait_for_result(task_id)
            else:
                # if async return taskid to allow query for status later on
                return [r.id for r in task_id.results]
        else:
            # By default execute the task directly without involving celery or a broker.
            # Return all results without raising exceptions.
            log.info('Executing task directly.')
            return self.task.apply(*self.args, **self.kwargs).get(propagate=False)

    def wait_for_result(self, task_id):
        """Wait for all (sub)tasks to complete and return result."""
        # wait for all tasks to be completed
        while not task_id.ready():
            # show intermediate status
            log.info('Task execution status: %s', dict(Counter([t.state for t in task_id.results])))
            time.sleep(self.interval)

        # return final results, don't reraise exceptions
        result = task_id.get(propagate=False)
        task_id.forget()
        return result


class ScannerTaskCommand(TaskCommand):
    """Generic Task Command for scanners."""

    scanner_module = None

    def _add_arguments(self, parser):
        """Add command specific arguments."""
        self.mutual_group.add_argument('-o', '--organization_names', nargs='*',
                                       help="Perform scans on these organizations (default is all).")

    def compose(self, *args, **options):
        """Compose set of tasks based on provided arguments."""

        if not options['organization_names']:
            # by default no filter means all organizations
            organization_filter = dict()
        else:
            # create a case-insensitive filter to match organizations by name
            regex = '^(' + '|'.join(options['organization_names']) + ')$'
            organization_filter = {'name__iregex': regex}

        # compose set of tasks to be executed
        return self.scanner_module.compose_task(organization_filter)
