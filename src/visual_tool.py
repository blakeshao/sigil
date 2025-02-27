
from typing import Any, Union, Optional, Callable
from langchain_core.messages.tool import ToolOutputMixin, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from inspect import signature
from langchain_core.runnables.config import _set_config_context
from contextvars import copy_context
from langchain_core.tools.base import (
    BaseTool,
    _get_runnable_config_param,
)
from langchain_core.runnables import (
    RunnableConfig,
    patch_config,
)
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
    CallbackManager,
    Callbacks
)
from pydantic import ValidationError
from collections.abc import Awaitable
import uuid
from pydantic.v1 import ValidationError as ValidationErrorV1
from pydantic.v1 import validate_arguments as validate_arguments_v1

class ToolException(Exception):  # noqa: N818
    """Optional exception that tool throws when execution error occurs.

    When this exception is thrown, the agent will not stop working,
    but it will handle the exception according to the handle_tool_error
    variable of the tool, and the processing result will be returned
    to the agent as observation, and printed in red on the console.
    """

class VisualTool(BaseTool):
    
    
    description: str = ""
    func: Optional[Callable[..., str]]
    """The function to run when the tool is called."""
    coroutine: Optional[Callable[..., Awaitable[str]]] = None

    def __init__(
        self, name: str, func: Optional[Callable], description: str, **kwargs: Any
    ) -> None:
        """Initialize tool."""
        super().__init__(  # type: ignore[call-arg]
            name=name, func=func, description=description, **kwargs
        )

  
    @staticmethod
    def _format_output(
        content: Any,
        artifact: Any,
        tool_call_id: Optional[str],
        name: str,
        status: str,
    ) -> Union[ToolOutputMixin, Any]:
        content = [{
                        "type": "image_url", 
                        "image_url": {
                            "url": content
                        }
                  }]
                
        # Save tool message content to a file
        message = ToolMessage(
            content,
            artifact=artifact,
            tool_call_id=tool_call_id if tool_call_id else "",
            name=name,
            status=status,
        )
        with open("tool_message.txt", "w", encoding="utf-8") as f:
            f.write(str(message))

        return message

    

    
    def _run(
        self,
        *args: Any,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Use the tool."""
        print(f"_run called with args: {args}, kwargs: {kwargs}")
        if self.func:
            if run_manager and signature(self.func).parameters.get("callbacks"):
                kwargs["callbacks"] = run_manager.get_child()
            if config_param := _get_runnable_config_param(self.func):
                kwargs[config_param] = config
            return self.func(*args, **kwargs)
        msg = "Tool does not support sync invocation."
        raise NotImplementedError(msg)
    
    
    def run(
        self,
        tool_input: Union[str, dict[str, Any]],
        verbose: Optional[bool] = None,
        start_color: Optional[str] = "green",
        color: Optional[str] = "green",
        callbacks: Callbacks = None,
        *,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        run_name: Optional[str] = None,
        run_id: Optional[uuid.UUID] = None,
        config: Optional[RunnableConfig] = None,
        tool_call_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Run the tool.

        Args:
            tool_input: The input to the tool.
            verbose: Whether to log the tool's progress. Defaults to None.
            start_color: The color to use when starting the tool. Defaults to 'green'.
            color: The color to use when ending the tool. Defaults to 'green'.
            callbacks: Callbacks to be called during tool execution. Defaults to None.
            tags: Optional list of tags associated with the tool. Defaults to None.
            metadata: Optional metadata associated with the tool. Defaults to None.
            run_name: The name of the run. Defaults to None.
            run_id: The id of the run. Defaults to None.
            config: The configuration for the tool. Defaults to None.
            tool_call_id: The id of the tool call. Defaults to None.
            kwargs: Keyword arguments to be passed to tool callbacks

        Returns:
            The output of the tool.

        Raises:
            ToolException: If an error occurs during tool execution.
        """
        callback_manager = CallbackManager.configure(
            callbacks,
            self.callbacks,
            self.verbose or bool(verbose),
            tags,
            self.tags,
            metadata,
            self.metadata,
        )

        run_manager = callback_manager.on_tool_start(
            {"name": self.name, "description": self.description},
            tool_input if isinstance(tool_input, str) else str(tool_input),
            color=start_color,
            name=run_name,
            run_id=run_id,
            # Inputs by definition should always be dicts.
            # For now, it's unclear whether this assumption is ever violated,
            # but if it is we will send a `None` value to the callback instead
            # TODO: will need to address issue via a patch.
            inputs=tool_input if isinstance(tool_input, dict) else None,
            **kwargs,
        )

        content = None
        artifact = None
        status = "success"
        error_to_raise: Union[Exception, KeyboardInterrupt, None] = None
        try:
            child_config = patch_config(config, callbacks=run_manager.get_child())
            context = copy_context()
            context.run(_set_config_context, child_config)
            tool_args, tool_kwargs = self._to_args_and_kwargs(tool_input, tool_call_id)
            if signature(self._run).parameters.get("run_manager"):
                tool_kwargs = tool_kwargs | {"run_manager": run_manager}
            if config_param := _get_runnable_config_param(self._run):
                tool_kwargs = tool_kwargs | {config_param: config}
            response = context.run(self._run, *tool_args, **tool_kwargs)
            if self.response_format == "content_and_artifact":
                if not isinstance(response, tuple) or len(response) != 2:
                    msg = (
                        "Since response_format='content_and_artifact' "
                        "a two-tuple of the message content and raw tool output is "
                        f"expected. Instead generated response of type: "
                        f"{type(response)}."
                    )
                    error_to_raise = ValueError(msg)
                else:
                    content, artifact = response
            else:
                content = response
        except (ValidationError, ValidationErrorV1) as e:
            if not self.handle_validation_error:
                error_to_raise = e
            else:
                content = super()._handle_validation_error(e, flag=self.handle_validation_error)
                status = "error"
        except ToolException as e:
            if not self.handle_tool_error:
                error_to_raise = e
            else:
                content = super()._handle_tool_error(e, flag=self.handle_tool_error)
                status = "error"
        except (Exception, KeyboardInterrupt) as e:
            error_to_raise = e

        if error_to_raise:
            run_manager.on_tool_error(error_to_raise)
            raise error_to_raise
        output = VisualTool._format_output(content, artifact, tool_call_id, self.name, status)
        run_manager.on_tool_end(output, color=color, name=self.name, **kwargs)
        return output

    