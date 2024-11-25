from typing import Type, Any, Optional, Coroutine

from langchain_community.tools import ClickTool
from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_community.tools.playwright.click import ClickToolInput
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel


class CustomClickTool(ClickTool, BaseBrowserTool):
    """Tool for clicking on an element with the given CSS selector."""

    name: str = "click_element"
    description: str = "Click on an element with the given CSS selector"
    args_schema: Type[BaseModel] = ClickToolInput

    visible_only: bool = False
    """Whether to consider only visible elements."""
    playwright_strict: bool = False
    """Whether to employ Playwright's strict mode when clicking on elements."""
    playwright_timeout: float = 1_000
    """Timeout (in ms) for Playwright to wait for element to be ready."""


    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _run(self, selector:str,  run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        result = super()._run(selector, run_manager)  # Call the original _run logic
        return result

    async def _arun(
        self, selector:str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> Coroutine[Any, Any, str]:
        result = super()._arun(selector, run_manager)
        return result