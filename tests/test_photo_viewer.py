import pytest

from telegram_mcp import runtime
from telegram_mcp.photo_viewer import PHOTO_VIEWER_URI
from telegram_mcp.tools import media


@pytest.mark.asyncio
async def test_photo_viewer_is_linked_to_existing_read_only_tool():
    tools = await runtime.mcp.list_tools()
    tool = next(tool for tool in tools if tool.name == "open_photo")
    assert tool.meta["ui"]["resourceUri"] == PHOTO_VIEWER_URI
    assert tool.meta["openai/outputTemplate"] == PHOTO_VIEWER_URI
    assert tool.annotations.readOnlyHint is True


@pytest.mark.asyncio
async def test_photo_viewer_resource_reads_without_contacting_telegram(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("UI resource must not read a session or call Telegram")

    monkeypatch.setattr(media, "get_client", forbidden)
    resources = await runtime.mcp.read_resource(PHOTO_VIEWER_URI)
    assert len(resources) == 1
    resource = resources[0]
    assert resource.mime_type == "text/html;profile=mcp-app"
    assert "ui/notifications/tool-result" in resource.content
    assert "data:image/jpeg;base64," in resource.content
