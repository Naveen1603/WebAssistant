from typing import List
from typing import cast

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,
    create_sync_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, typing

from app.agent.tools.extract_text_tool import CustomExtractTextTool
from app.playwright.custom_toolkit import CustomPlayWrightBrowserToolkit


class BrowserToolkit:
    def __init__(self):
        self.async_browser = create_async_playwright_browser(headless=False)
        # self.sync_browser = create_sync_playwright_browser(headless=False)
        self.toolkit = CustomPlayWrightBrowserToolkit.from_browser(async_browser=self.async_browser)
        self.tools = self.toolkit.get_tools()
        # self.custom_extract_text_tool = ExtractTextTool.from_browser(sync_browser=self.sync_browser, async_browser=self.async_browser)


    def get_tools(self):
        all_tools = [tool.name for tool in self.tools]
        can_be_processed_tools = []
        for tool in self.tools:# + typing.cast(List[BaseTool], [self.custom_extract_text_tool]):
            try:
                cast = str(tool.args)
                can_be_processed_tools.append(tool)
            except:
                pass
        loaded_tools = [tool.name for tool in can_be_processed_tools]
        print(f"Tools Available: {all_tools}, Tools Loaded: {loaded_tools}")
        return can_be_processed_tools


