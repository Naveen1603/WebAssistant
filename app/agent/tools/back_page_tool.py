from typing import Any, Type, Optional, Coroutine

from langchain_community.tools import CurrentWebPageTool
from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel

from app.agent.tools.empty_pydantic_input import EmptyPydanticToolInput

class CustomNavigateBackTool(CurrentWebPageTool, BaseBrowserTool):
    """Navigate back to the previous page in the browser history."""

    name: str = "previous_webpage"
    description: str = "Navigate back to the previous page in the browser history"
    args_schema: Type[BaseModel] = EmptyPydanticToolInput
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        result = super()._run(run_manager)  # Call the original _run logic
        return result

    async def _arun(
        self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> Coroutine[Any, Any, str]:
        result = super()._arun(run_manager)
        return result



