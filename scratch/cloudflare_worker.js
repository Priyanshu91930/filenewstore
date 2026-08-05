class XorTransformStream {
  constructor(key = 0x5A) {
    this.key = key;
    this.key32 = (key << 24) | (key << 16) | (key << 8) | key;
  }

  transform(chunk, controller) {
    const len = chunk.length;
    if (len === 0) return;

    const byteOffset = chunk.byteOffset;
    if (byteOffset % 4 === 0) {
      const u32len = Math.floor(len / 4);
      const u32view = new Uint32Array(chunk.buffer, byteOffset, u32len);
      for (let i = 0; i < u32len; i++) {
        u32view[i] ^= this.key32;
      }
      for (let i = u32len * 4; i < len; i++) {
        chunk[i] ^= this.key;
      }
    } else {
      for (let i = 0; i < len; i++) {
        chunk[i] ^= this.key;
      }
    }
    controller.enqueue(chunk);
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/stream' || url.pathname === '/play' || url.pathname.endsWith('.mp4')) {
      const fileId = url.searchParams.get('fileId') || url.searchParams.get('fileid') || url.searchParams.get('id') || url.searchParams.get('fileld');
      if (!fileId) {
        return new Response('Missing fileId parameter', { status: 400 });
      }

      const gdriveUrl = `https://drive.google.com/uc?export=download&id=${fileId}`;

      // Forward target headers (including Range header required by ExoPlayer/Android)
      const requestHeaders = new Headers();
      requestHeaders.set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

      const range = request.headers.get('Range');
      if (range) {
        requestHeaders.set('Range', range);
      }

      try {
        let driveResponse = await fetch(gdriveUrl, {
          method: 'GET',
          headers: requestHeaders,
          redirect: 'follow'
        });

        // If Google Drive returns a virus warning HTML page (common for files >100MB),
        // extract the confirmation token and fetch the actual stream.
        const contentType = driveResponse.headers.get('content-type') || '';
        if (contentType.includes('text/html') && driveResponse.status === 200) {
          const htmlText = await driveResponse.text();
          // Match confirm token: e.g. confirm=xxxx or confirm=t, or in the new form inputs
          const tokenMatch = htmlText.match(/confirm=([a-zA-Z0-9-_]+)/) || 
                             htmlText.match(/name="confirm"\s+value="([^"]+)"/) ||
                             htmlText.match(/value="([^"]+)"\s+name="confirm"/) ||
                             htmlText.match(/id="confirm"[^>]*value="([^"]+)"/);
          if (tokenMatch && tokenMatch[1]) {
            const confirmToken = tokenMatch[1];
            const confirmUrl = `https://drive.google.com/uc?export=download&id=${fileId}&confirm=${confirmToken}`;

            const confirmHeaders = new Headers(requestHeaders);
            const setCookie = driveResponse.headers.get('set-cookie');
            if (setCookie) {
              confirmHeaders.set('Cookie', setCookie);
            }

            driveResponse = await fetch(confirmUrl, {
              method: 'GET',
              headers: confirmHeaders,
              redirect: 'manual'
            });

            if (
              driveResponse.status === 301 ||
              driveResponse.status === 302 ||
              driveResponse.status === 303 ||
              driveResponse.status === 307 ||
              driveResponse.status === 308
            ) {
              const redirectUrl = driveResponse.headers.get('Location');
              if (redirectUrl) {
                driveResponse = await fetch(redirectUrl, {
                  method: 'GET',
                  headers: requestHeaders
                });
              }
            }
          } else {
            return new Response(`Failed to parse confirm token. Status: ${driveResponse.status}, Content-Type: ${contentType}. HTML Snippet: ${htmlText.substring(0, 2000)}`, {
              status: 500,
              headers: { "Content-Type": "text/plain" }
            });
          }
        }

        const originalContentType = driveResponse.headers.get('Content-Type') || driveResponse.headers.get('content-type') || '';
        const disposition = driveResponse.headers.get('Content-Disposition') || '';
        const isEncrypted = originalContentType.includes('octet-stream') || 
                            originalContentType.includes('download') || 
                            disposition.includes('.dat');

        // Setup headers to return to the Android Player
        const responseHeaders = new Headers();
        let contentTypeHeader = originalContentType || 'video/mp4';
        if (contentTypeHeader.includes('text/html') || contentTypeHeader.includes('octet-stream') || contentTypeHeader.includes('download')) {
          contentTypeHeader = 'video/mp4';
        }
        responseHeaders.set('Content-Type', contentTypeHeader);
        responseHeaders.set('Content-Disposition', 'inline');
        responseHeaders.set('Accept-Ranges', 'bytes');
        responseHeaders.set('Access-Control-Allow-Origin', '*');
        responseHeaders.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
        responseHeaders.set('Access-Control-Allow-Headers', 'Range, Content-Type');

        // Pass down Content-Range and Content-Length if present for ExoPlayer seek parsing
        const contentRange = driveResponse.headers.get('Content-Range');
        if (contentRange) {
          responseHeaders.set('Content-Range', contentRange);
        }
        const contentLength = driveResponse.headers.get('Content-Length');
        if (contentLength) {
          responseHeaders.set('Content-Length', contentLength);
        }

        if (request.method === 'OPTIONS') {
          return new Response(null, {
            status: 204,
            headers: responseHeaders
          });
        }

        // XOR Decrypt raw bytes dynamically only if the file is encrypted
        let responseBody = driveResponse.body;
        if (responseBody && isEncrypted && (driveResponse.status === 200 || driveResponse.status === 206)) {
          const decryptor = new TransformStream(new XorTransformStream(0x5A));
          responseBody = responseBody.pipeThrough(decryptor);
        }

        return new Response(responseBody, {
          status: driveResponse.status,
          statusText: driveResponse.statusText,
          headers: responseHeaders
        });

      } catch (error) {
        return new Response(`Worker Stream Exception: ${error.message}`, { status: 500 });
      }
    }

    return new Response('Not Found. Use /stream?fileId=YOUR_FILE_ID to play videos.', { status: 404 });
  }
};
