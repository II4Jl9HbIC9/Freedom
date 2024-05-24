from __future__ import annotations

import collections
import contextlib
import importlib
import types
import typing

import typing_extensions

from freedom import util
from freedom.domain import command as command_
from freedom.domain import command_handler as command_handler_
from freedom.domain import event as event_
from freedom.domain import event_handler as event_handler_
from freedom.domain import repository as repository_

if typing.TYPE_CHECKING:
    from freedom.application import command_bus as command_bus_
    from freedom.application import event_emitter as event_emitter_
    from freedom.application import provider

_CallableT = typing.TypeVar("_CallableT", bound=typing.Callable[..., typing.Any])
_ResultT = typing.TypeVar("_ResultT", bound=command_handler_.CommandResult)


def collect_domain_events(
    result: _ResultT,
    kwargs: typing.Mapping[str, typing.Any],
) -> _ResultT:
    repositories = typing.cast(
        typing.Iterable[repository_.AnyRepository],
        filter(lambda x: isinstance(x, repository_.Repository), kwargs.values()),
    )
    domain_events = []
    for repository in repositories:
        domain_events.extend(repository.collect_events())

    result.events.extend(domain_events)
    return result


class TransactionContext:
    def __init__(
        self,
        application: Application,
        command_bus: command_bus_.CommandBus,
        dependency_provider: typing.Optional[provider.AnyDependencyProviderType] = None,
        event_emitter: typing.Optional[event_emitter_.EventEmitter] = None,
    ) -> None:
        self._application = application
        self._event_emitter = event_emitter
        self._command_bus = command_bus
        self._dependency_provider = dependency_provider

        # ... declaration explanation
        self._executing_task: bool = False

    def __enter__(self) -> typing_extensions.Self:
        self._application._on_enter_transaction_context(self)
        return self

    @typing.overload
    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None: ...

    @typing.overload
    def __exit__(
        self,
        exc_type: typing.Type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None: ...

    @typing.no_type_check
    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None:
        self._application._on_exit_transaction_context(self, exc_type, exc_val, exc_tb)

    async def execute_command(
        self, command: command_.Command
    ) -> command_handler_.CommandResult:
        with self._lock_transaction():
            command_result = await self._command_bus.execute(command)

            event_queue = command_result.events.copy()
            while len(event_queue) > 0:
                event = event_queue.pop(0)

                if isinstance(event, event_.Event):
                    # Чтобы в дальнейшем реализовать интеграционные ивенты in-box & out-box pattern
                    await self.handle_domain_event(event)
                    # event_results = await self.handle_domain_event(event)
                    # event_queue.extend(event_results.events)

            if command_result.is_success():
                result = command_handler_.CommandResult.success(
                    entity_id=command_result.entity_id,
                    events=command_result.events,
                )
            else:
                # FIXME: пока что берем только первую ошибку
                err = command_result.errors[0]
                result = command_handler_.CommandResult.failure(
                    fail_message=err.message,
                    exception=err.exception,
                    exception_info=err.exception_info,
                )

            return result

    async def handle_domain_event(self, event: event_.Event) -> None:
        if self._event_emitter is None:
            raise ValueError(
                "Event emitter is not set, when event sourced aggregate is used."
            )
        await self._event_emitter.emit(event)

    def get_service(self, service_cls: typing.Any) -> typing.Any:
        if self._dependency_provider is None:
            raise ValueError("Application does not have dependency provider.")
        return self._dependency_provider.get_dependency(service_cls)

    @contextlib.contextmanager
    def _lock_transaction(self) -> typing.Iterator[None]:
        if self._executing_task:
            raise RuntimeError(
                "Cannot execute command while another task is being executed."
            )

        self._executing_task = True
        yield
        self._executing_task = False


class ApplicationModule:
    __slots__: typing.Sequence[str] = (
        "_name",
        "_version",
        "_command_handlers",
        "_event_handlers",
        "_query_handlers",
    )

    def __init__(self, name: str, version: float) -> None:
        self._name = name
        self._version = version
        self._command_handlers: typing.Dict[
            typing.Type[command_.Command],
            command_handler_.AnyCommandHandlerType,
        ] = {}
        self._event_handlers: typing.Dict[
            typing.Type[event_.Event], typing.List[event_handler_.AnyEventHandlerType]
        ] = collections.defaultdict(list)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> float:
        return self._version

    def load(self, path: str) -> None:
        importlib.import_module(path)

    def with_command_handler(
        self,
        handler: command_handler_.AnyCommandHandlerType,
        command_cls: typing.Optional[command_.CommandType] = None,
    ) -> typing_extensions.Self:
        if (command := command_cls) is None:
            command, *_ = util.get_type_hints(
                handler.__init__,
                subclass_of=(command_handler_.CommandHandler,),
            ).values()

        self._command_handlers[command] = handler
        return self

    def with_event_handler(
        self,
        handler: event_handler_.AnyEventHandlerType,
        event_cls: typing.Optional[event_.EventType] = None,
    ) -> typing_extensions.Self:
        if (event := event_cls) is None:
            event, *_ = util.get_type_hints(
                handler.__init__,
                subclass_of=(event_handler_.EventHandler,),
            ).values()

        self._event_handlers[event].append(handler)
        return self

    def event_handler(
        self,
        event_cls: typing.Optional[event_.EventType] = None,
    ) -> typing.Callable[
        [event_handler_.AnyEventHandlerTypeT], event_handler_.AnyEventHandlerTypeT
    ]:
        def decorator(
            handler: event_handler_.AnyEventHandlerTypeT,
        ) -> event_handler_.AnyEventHandlerTypeT:
            self.with_event_handler(handler, event_cls)
            return handler

        return decorator

    def command_handler(
        self,
        command_cls: typing.Optional[command_.CommandType] = None,
    ) -> typing.Callable[
        [command_handler_.AnyCommandHandlerTypeT],
        command_handler_.AnyCommandHandlerTypeT,
    ]:
        def decorator(
            handler: command_handler_.AnyCommandHandlerTypeT,
        ) -> command_handler_.AnyCommandHandlerTypeT:
            self.with_command_handler(handler, command_cls)
            return handler

        return decorator


class Application(ApplicationModule):
    def __init__(
        self,
        name: str,
        version: float,
        *,
        command_bus: command_bus_.CommandBus,
        dependency_provider: typing.Optional[provider.AnyDependencyProviderType] = None,
        event_emitter: typing.Optional[event_emitter_.EventEmitter] = None,
    ) -> None:
        super().__init__(name, version)
        self._command_bus = command_bus
        self._event_emitter = event_emitter
        self._dependency_provider = dependency_provider
        self._on_enter_transaction_context: typing.Callable[
            [TransactionContext], None
        ] = lambda ctx: None
        self._on_exit_transaction_context: typing.Callable[..., None] = (
            lambda ctx, exc_type, exc_val, exc_tb: None
        )
        self._modules: typing.Set[ApplicationModule] = {self}

    def include_module(self, module: ApplicationModule) -> None:
        if not isinstance(module, ApplicationModule):
            raise TypeError("Can only include ApplicationModule instances")

        # FIXME: event handlers, ... , etc
        for command, command_handler in module._command_handlers.items():
            self._command_bus.subscribe(command_handler, command)

        if self._event_emitter is not None:
            for event, event_handlers in module._event_handlers.items():
                for handler in event_handlers:
                    self._event_emitter.subscribe(handler, event)

        self._modules.add(module)

    def on_enter_transaction_context(self, callable_: _CallableT) -> _CallableT:
        self._on_enter_transaction_context = callable_
        return callable_

    def on_exit_transaction_context(self, callable_: _CallableT) -> _CallableT:
        self._on_exit_transaction_context = callable_
        return callable_

    def get_command_handler(
        self, command: command_.Command
    ) -> command_handler_.AnyCommandHandlerType:
        command_cls = type(command)
        for app_module in self._modules:
            handler_func = app_module._command_handlers.get(command_cls)
            if handler_func is not None:
                return handler_func

        raise KeyError(f"No command handler found for command {command_cls}")

    def get_event_handlers(
        self, event: event_.Event
    ) -> typing.List[event_handler_.AnyEventHandlerType]:
        event_cls = type(event)
        event_handlers = []
        for app_module in self._modules:
            event_handlers.extend(app_module._event_handlers.get(event_cls, []))

        return event_handlers

    def transaction_context(self) -> TransactionContext:
        ctx = TransactionContext(
            self,
            command_bus=self._command_bus,
            event_emitter=self._event_emitter,
            dependency_provider=self._dependency_provider,
        )
        return ctx

    async def execute_command(
        self, command: command_.Command
    ) -> command_handler_.CommandResult:
        with self.transaction_context() as ctx:
            return await ctx.execute_command(command)
