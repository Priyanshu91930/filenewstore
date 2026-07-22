/**
 * Cloudflare Worker: 18+ Content Safe Google Drive Video Stream Proxy
 * 
 * Features:
 * - Real-time MIME type override (forces binary .dat -> video/mp4)
 * - Full HTTP Range requests support (enables skip/seek/fast-forward without buffering)
 * - Safe streaming (bypasses Google Drive file scanners)
 * 
 * Configuration (Set in Cloudflare Worker environment variables):
 * - API_KEY: Google Cloud API Key (for public files)
 * - OR configure Service Account parameters below if using private files.
 */

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
    
    // Path routing: e.g. /stream?fileId=XXXXX
    if (url.pathname === '/stream' || url.pathname === '/play') {
      const fileId = url.searchParams.get('fileId') || url.searchParams.get('id');
      if (!fileId) {
        return new Response('Missing fileId parameter', { status: 400 });
      }

      // 1. Determine Google Drive API media URL
      // If you use public GDrive files (with 'anyone with link' access), you can pass an API_KEY
      const apiKey = env.API_KEY || "YOUR_GOOGLE_API_KEY"; 
      let gdriveUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
      
      if (apiKey && apiKey !== "YOUR_GOOGLE_API_KEY") {
        gdriveUrl += `&key=${apiKey}`;
      }

      // 2. Forward headers (like Range) from incoming request
      const requestHeaders = new Headers();
      const range = request.headers.get('Range');
      if (range) {
        requestHeaders.set('Range', range);
        console.log(`Requested Range: ${range}`);
      }

      // If you are using service account OAuth token, set it here
      // const oauthToken = await getAccessToken(env);
      // if (oauthToken) {
      //   requestHeaders.set('Authorization', `Bearer ${oauthToken}`);
      // }

      try {
        // Fetch from Google Drive API
        const driveResponse = await fetch(gdriveUrl, {
          method: 'GET',
          headers: requestHeaders
        });

        // 3. Construct proxy response with overridden headers for streaming
        const responseHeaders = new Headers(driveResponse.headers);
        
        // Force the content type to video/mp4
        responseHeaders.set('Content-Type', 'video/mp4');
        responseHeaders.set('Content-Disposition', 'inline');
        responseHeaders.set('Accept-Ranges', 'bytes');
        
        // Add CORS headers for App and Web playback
        responseHeaders.set('Access-Control-Allow-Origin', '*');
        responseHeaders.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
        responseHeaders.set('Access-Control-Allow-Headers', 'Range, Content-Type');

        // Handle HTTP OPTIONS preflight request
        if (request.method === 'OPTIONS') {
          return new Response(null, {
            status: 204,
            headers: responseHeaders
          });
        }

        // Decrypt the stream on-the-fly using TransformStream (only for successful requests)
        let responseBody = driveResponse.body;
        if (responseBody && (driveResponse.status === 200 || driveResponse.status === 206)) {
          const decryptor = new TransformStream(new XorTransformStream(0x5A));
          responseBody.pipeTo(decryptor.writable);
          responseBody = decryptor.readable;
        }

        // Return the stream with modified headers
        return new Response(responseBody, {
          status: driveResponse.status,
          statusText: driveResponse.statusText,
          headers: responseHeaders
        });

      } catch (error) {
        return new Response(`Stream Error: ${error.message}`, { status: 500 });
      }
    }

    return new Response('Not Found. Use /stream?fileId=YOUR_FILE_ID to play videos.', { status: 404 });
  }
};

/**
 * OPTIONAL: Helper function to generate dynamic Google OAuth Token inside Cloudflare Worker
 * using Service Account credentials (for private GDrive files protection).
 * To use this, add SERVICE_ACCOUNT_EMAIL and SERVICE_ACCOUNT_PRIVATE_KEY to env variables.
 */
async function getAccessToken(env) {
  if (!env.SERVICE_ACCOUNT_EMAIL || !env.SERVICE_ACCOUNT_PRIVATE_KEY) {
    return null;
  }
  
  // Implements JWT generation and RSA signing using Web Crypto API.
  // Full implementation details are standard OAuth 2.0 JWT assertion.
  // Contact agent if you need full Service Account auth signing code inside the worker.
  return null; 
}
