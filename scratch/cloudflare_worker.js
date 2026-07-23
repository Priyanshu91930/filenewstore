class XorTransformStream {
  constructor(key = 0x5A) {
    this.key = key;
  }

  transform(chunk, controller) {
    const decrypted = new Uint8Array(chunk.length);
    for (let i = 0; i < chunk.length; i++) {
      decrypted[i] = chunk[i] ^ this.key;
    }
    controller.enqueue(decrypted);
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

      const gdriveUrl = `https://docs.google.com/uc?export=download&id=${fileId}`;

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
          // Match confirm token: e.g. confirm=xxxx or confirm=t
          const tokenMatch = htmlText.match(/confirm=([a-zA-Z0-9-_]+)/);
          if (tokenMatch && tokenMatch[1]) {
            const confirmToken = tokenMatch[1];
            const confirmUrl = `https://docs.google.com/uc?export=download&id=${fileId}&confirm=${confirmToken}`;
            driveResponse = await fetch(confirmUrl, {
              method: 'GET',
              headers: requestHeaders,
              redirect: 'follow'
            });
          }
        }

        // Setup headers to return to the Android Player
        const responseHeaders = new Headers();
        let contentTypeHeader = driveResponse.headers.get('Content-Type') || driveResponse.headers.get('content-type') || 'video/mp4';
        if (contentTypeHeader.includes('text/html')) {
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

        // XOR Decrypt raw bytes dynamically
        let responseBody = driveResponse.body;
        if (responseBody && (driveResponse.status === 200 || driveResponse.status === 206)) {
          const decryptor = new TransformStream(new XorTransformStream(0x5A));
          responseBody.pipeTo(decryptor.writable);
          responseBody = decryptor.readable;
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
