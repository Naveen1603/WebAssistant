from typing import Any, Type, Optional, Coroutine

from langchain_community.tools import ExtractTextTool
from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel

from app.agent.tools.empty_pydantic_input import EmptyPydanticToolInput


class CustomExtractTextTool(ExtractTextTool, BaseBrowserTool):
    """Tool for extracting all the text on the current webpage. NOTE:- action_input for this tool was always None and before extract text the browser needs to be navigated to the page"""

    name: str = "extract_text"
    description: str = "Extract all the text on the current webpage"
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



