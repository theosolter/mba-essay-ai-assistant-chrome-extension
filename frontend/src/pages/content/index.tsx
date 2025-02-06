import { createRoot } from 'react-dom/client';
import { MbaEssayAssistant } from '@/components/MbaEssayAssistant';
import '@assets/styles/tailwind.css';

// Types for messages that can be received from the popup
interface ChromeMessage {
  action: 'showSidebar' | 'hideSidebar' | 'getEssayContent';
}

console.log("[Content Script] Initializing...");

// Handle messages from the popup
chrome.runtime.onMessage.addListener((request: ChromeMessage, sender, sendResponse) => {
  try {
    switch (request.action) {
      case 'showSidebar':
        injectSidebar();
        showSidebar();
        break;
      case 'hideSidebar':
        hideSidebar();
        break;
    }
    sendResponse({ success: true });
  } catch (error) {
    console.error('Error handling message:', error);
    sendResponse({ success: false, error: (error as Error).message });
  }

  return true; // Required for async response
});

// Initialize sidebar based on stored state when content script loads
chrome.storage.sync.get(['sidebarEnabled'], (result) => {
  if (result.sidebarEnabled) {
    injectSidebar();
    showSidebar();
  }
});

/**
 * Creates and injects the sidebar container into the page if it doesn't already exist.
 * The sidebar is initially hidden (translated off-screen) and includes the React component.
 * This function is called in response to popup messages or initial state.
 */
function injectSidebar(): void {
  const SIDEBAR_ID = 'mba-essay-assistant-sidebar';
  const SIDEBAR_WIDTH = '500px';

  if (document.getElementById(SIDEBAR_ID)) {
    return;
  }

  const sidebarContainer = document.createElement('div');
  sidebarContainer.id = SIDEBAR_ID;
  
  // Set up sidebar styling
  Object.assign(sidebarContainer.style, {
    position: 'fixed',
    top: '0',
    right: '0',
    height: '100vh',
    width: SIDEBAR_WIDTH,
    zIndex: '10000',
    backgroundColor: 'white',
    boxShadow: '-2px 0 5px rgba(0,0,0,0.2)',
    transition: 'transform 0.3s ease',
    transform: 'translateX(100%)'
  });

  document.body.appendChild(sidebarContainer);
  document.body.style.paddingRight = SIDEBAR_WIDTH;

  // Render React component in sidebar
  const sidebarRoot = createRoot(sidebarContainer);
  sidebarRoot.render(<MbaEssayAssistant />);
}

/**
 * Shows the sidebar by translating it into view and adjusting the page padding.
 * This function is called in response to popup messages or initial state.
 */
function showSidebar(): void {
  const sidebar = document.getElementById('mba-essay-assistant-sidebar');
  if (sidebar) {
    sidebar.style.transform = 'translateX(0)';
    const width = sidebar.offsetWidth;
    document.body.style.paddingRight = `${width}px`;
  } else {
    console.warn('Sidebar element not found');
  }
}

/**
 * Hides the sidebar by translating it off-screen and removing the page padding.
 * This function is called in response to popup messages.
 */
function hideSidebar(): void {
  const sidebar = document.getElementById('mba-essay-assistant-sidebar');
  if (sidebar) {
    sidebar.style.transform = 'translateX(100%)';
    document.body.style.paddingRight = '0';
  } else {
    console.warn('Sidebar element not found');
  }
}