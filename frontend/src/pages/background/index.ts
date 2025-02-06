// Type definitions for user data and authentication
interface User {
  email: string;
  name: string;
}

interface AuthResponse {
  token: string;
  user: User;
}

// Types for message communication between extension components
interface MessageResponse {
  success: boolean;
  error?: string;
  user?: User;
  content?: string;
}

// Types for Google Docs API response structure
interface GoogleDoc {
  body: {
    content: Array<DocContent>;
  };
}

interface DocContent {
  paragraph?: {
    elements: Array<{
      textRun?: {
        content: string;
      };
    }>;
  };
  table?: {
    tableRows: Array<{
      tableCells: Array<{
        content: Array<DocContent>;
      }>;
    }>;
  };
}

// Type definition for message handler functions
type MessageHandler = (
  request: { action: 'signIn' | 'signOut' | 'getEssayContent' },
  sender: chrome.runtime.MessageSender,
  sendResponse: (response: MessageResponse) => void
) => boolean | void;

/**
 * Validates a Google OAuth token by making a request to Google's tokeninfo endpoint
 */
async function validateToken(token: string): Promise<boolean> {
  try {
    const response = await fetch(`https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${token}`);
    return response.ok;
  } catch (error) {
    console.error('Token validation failed:', error);
    return false;
  }
}

/**
 * Fetches user information from Google's userinfo endpoint using the provided token
 */
async function getUserInfo(token: string): Promise<User> {
  const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch user info');
  }
  
  const userData = await response.json();
  return {
    email: userData.email,
    name: userData.name
  };
}

/**
 * Handles the Google authentication flow, including token validation and user info fetching.
 * If interactive is true, shows the Google sign-in popup, otherwise uses cached credentials.
 */
async function handleAuthentication(interactive: boolean = false): Promise<AuthResponse> {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive }, async (token) => {
      if (chrome.runtime.lastError || !token) {
        console.error('Auth error:', chrome.runtime.lastError);
        reject(chrome.runtime.lastError || new Error('No token received'));
        return;
      }

      try {
        const isValid = await validateToken(token);
        if (!isValid) {
          await chrome.identity.removeCachedAuthToken({ token });
          if (interactive) {
            return handleAuthentication(true);
          }
          throw new Error('Invalid token');
        }

        const user = await getUserInfo(token);
        
        await updateAuthState(true, user);

        resolve({ token, user });
      } catch (error) {
        console.error('Authentication failed:', error);
        reject(error);
      }
    });
  });
}

/**
 * Fetches and extracts the text content from a Google Doc using its ID
 */
async function getDocContent(docId: string): Promise<string> {
  try {
    const { token } = await handleAuthentication(false);
    const response = await fetch(
      `https://docs.googleapis.com/v1/documents/${docId}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch document');
    }

    const doc: GoogleDoc = await response.json();
    let content = '';
    
    /**
     * Recursively extracts text from the document's content structure
     * Handles both paragraphs and tables
     */
    function extractText(element: DocContent): void {
      if (element.paragraph) {
        element.paragraph.elements.forEach(elem => {
          if (elem.textRun) {
            content += elem.textRun.content;
          }
        });
      } else if (element.table) {
        element.table.tableRows.forEach(row => {
          row.tableCells.forEach(cell => {
            cell.content.forEach(extractText);
          });
        });
      }
    }

    doc.body.content.forEach(extractText);
    return content;
  } catch (error) {
    console.error('Error fetching document:', error);
    throw error;
  }
}

/**
 * Updates the authentication state in chrome.storage.local with the current sign-in status
 */
async function updateAuthState(isSignedIn: boolean, user: User | null): Promise<void> {
  await chrome.storage.local.set({
    isSignedIn,
    user,
    lastAuthTime: isSignedIn ? Date.now() : null
  });
}

// Periodic authentication check (every 5 minutes)
const AUTH_CHECK_INTERVAL = 5 * 60 * 1000;
setInterval(async () => {
  try {
    const { isSignedIn } = await chrome.storage.local.get('isSignedIn');
    if (isSignedIn) {
      await handleAuthentication(false);
    }
  } catch (error) {
    console.error('Auth check failed:', error);
    await updateAuthState(false, null);
  }
}, AUTH_CHECK_INTERVAL);

// Initialize extension state on install/update
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install" || details.reason === "update") {
    chrome.storage.local.set({
      sidebarEnabled: true,
      isSignedIn: false,
      user: null
    });
  }
});

// Attempt to restore authentication state on extension startup
chrome.runtime.onStartup.addListener(async () => {
  try {
    await handleAuthentication(false);
  } catch (error) {
    console.error('Failed to restore auth state:', error);
    await updateAuthState(false, null);
  }
});

/**
 * Handles messages from other parts of the extension.
 * Supports: signIn, signOut, and getEssayContent actions
 */
const messageHandler: MessageHandler = (request, sender, sendResponse) => {
  switch (request.action) {
    case "signIn":
      handleAuthentication(true)
        .then(({ user }) => sendResponse({ success: true, user }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;

    case "signOut":
      chrome.identity.getAuthToken({ interactive: false }, async (token) => {
        if (token) {
          await fetch(`https://accounts.google.com/o/oauth2/revoke?token=${token}`);
          await chrome.identity.removeCachedAuthToken({ token });
        }
        await updateAuthState(false, null);
        sendResponse({ success: true });
      });
      return true;

    case "getEssayContent":
      const docId = extractDocId(sender.tab?.url || '');
      if (!docId) {
        sendResponse({ success: false, error: 'Could not determine document ID' });
        return true;
      }

      getDocContent(docId)
        .then(content => sendResponse({ success: true, content }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;

    default:
      sendResponse({ success: false, error: 'Unknown action' });
      return false;
  }
};

/**
 * Extracts the Google Doc ID from a Google Docs URL
 */
function extractDocId(url: string): string | null {
  const matches = url.match(/\/document\/d\/([a-zA-Z0-9-_]+)/);
  return matches?.[1] || null;
}

// Register message handler
chrome.runtime.onMessage.addListener(messageHandler);