"""A private MCP Apps viewer for the image already returned by open_photo."""

PHOTO_VIEWER_URI = "ui://telegram/photo-viewer-v1.html"
PHOTO_VIEWER_META = {
    "ui": {"resourceUri": PHOTO_VIEWER_URI},
    "openai/outputTemplate": PHOTO_VIEWER_URI,
}

PHOTO_VIEWER_HTML = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Telegram photo</title>
<style>
body{margin:0;padding:12px;font:14px system-ui;color:inherit;background:transparent}
img{display:block;max-width:100%;height:auto;margin:auto;border-radius:8px}
p{margin:8px 0} [hidden]{display:none!important}
</style></head><body>
<p id="status" role="status">Loading photo…</p>
<img id="photo" alt="Photo returned by Telegram" hidden>
<script>
(() => {
  const photo = document.getElementById('photo');
  const status = document.getElementById('status');
  function render(result) {
    const image = (result?.content || []).find(item => item.type === 'image');
    if (!image) {
      status.textContent = 'No photo was returned. Check the tool response.';
      photo.hidden = true;
      return;
    }
    if (image.mimeType !== 'image/jpeg' ||
        typeof image.data !== 'string' ||
        !/^[A-Za-z0-9+/]+={0,2}$/.test(image.data)) {
      status.textContent = 'Invalid image response.';
      photo.hidden = true;
      return;
    }
    photo.onload = () => { photo.hidden = false; status.hidden = true; };
    photo.onerror = () => {
      photo.hidden = true; status.hidden = false;
      status.textContent = 'The returned image could not be decoded.';
    };
    // Bytes stay inside the existing tool result; no fetch or external hosting.
    photo.src = 'data:image/jpeg;base64,' + image.data;
  }
  window.addEventListener('message', event => {
    if (event.source !== window.parent) return;
    const message = event.data;
    if (!message || message.jsonrpc !== '2.0') return;
    if (message.id === 'photo-viewer-init' && message.result) {
      window.parent.postMessage({jsonrpc:'2.0',method:'ui/notifications/initialized'}, '*');
    }
    if (message.method === 'ui/notifications/tool-result') render(message.params);
  });
  window.parent.postMessage({
    jsonrpc:'2.0', id:'photo-viewer-init', method:'ui/initialize',
    params:{appInfo:{name:'Telegram photo viewer',version:'1.0.0'},
            appCapabilities:{},protocolVersion:'2026-01-26'}
  }, '*');
})();
</script></body></html>"""
