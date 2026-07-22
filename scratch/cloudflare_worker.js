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

      // We use Google Drive direct export download proxy bypass url
      const gdriveUrl = `https://docs.google.com/uc?export=download&id=${fileId}`;

      try {
        const driveResponse = await fetch(gdriveUrl, {
          method: 'GET',
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
          },
          redirect: 'follow'
        });

        // Set Response Headers
        const responseHeaders = new Headers();
        responseHeaders.set('Content-Type', 'video/mp4');
        responseHeaders.set('Content-Disposition', 'inline');
        responseHeaders.set('Access-Control-Allow-Origin', '*');
        responseHeaders.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
        responseHeaders.set('Access-Control-Allow-Headers', 'Range, Content-Type');

        if (request.method === 'OPTIONS') {
          return new Response(null, {
            status: 204,
            headers: responseHeaders
          });
        }

        // XOR Decrypt raw bytes 
        let responseBody = driveResponse.body;
        if (responseBody && (driveResponse.status === 200 || driveResponse.status === 206 || driveResponse.status === 302)) {
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
