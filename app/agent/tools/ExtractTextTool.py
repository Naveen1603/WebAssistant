from typing import Any, Type, Optional, Coroutine

from langchain_community.tools import ExtractTextTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from pydantic import BaseModel

class ExtractHyperlinksToolInput(BaseModel):
    """Input for ExtractHyperlinksTool."""
    pass

class CustomExtractTextTool(ExtractTextTool):
    name: str = "extract_text"
    description: str = "Extract all the text on the current webpage"
    args_schema: Type[BaseModel] = ExtractHyperlinksToolInput
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



