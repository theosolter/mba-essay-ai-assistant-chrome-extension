import { useEffect, useState } from "react"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

interface User {
  name: string
  email: string
}

interface StorageChanges {
  [key: string]: chrome.storage.StorageChange
}

/**
 * Popup component for the Chrome extension.
 * Handles user authentication state and sidebar visibility controls.
 */
export function Popup() {
  const [isSidebarEnabled, setIsSidebarEnabled] = useState(false)
  const [isSignedIn, setIsSignedIn] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Initialize state from Chrome storage
    const initializeState = async () => {
      const result = await chrome.storage.local.get([
        "sidebarEnabled",
        "isSignedIn",
        "user"
      ])
      setIsSidebarEnabled(result.sidebarEnabled ?? false)
      setIsSignedIn(result.isSignedIn ?? false)
      setUser(result.user ?? null)
      setIsLoading(false)
    }

    // Listen for auth state changes from other extension contexts
    const handleStorageChange = (changes: StorageChanges) => {
      if (changes.isSignedIn) {
        setIsSignedIn(changes.isSignedIn.newValue)
      }
      if (changes.user) {
        setUser(changes.user.newValue)
      }
    }

    initializeState()
    chrome.storage.local.onChanged.addListener(handleStorageChange)
    
    return () => {
      chrome.storage.local.onChanged.removeListener(handleStorageChange)
    }
  }, [])

  /**
   * Toggles the sidebar visibility and updates storage/tab state
   */
  const handleSidebarToggle = async (checked: boolean) => {
    setIsSidebarEnabled(checked)
    await chrome.storage.local.set({ sidebarEnabled: checked })
  
    try {
      const [activeTab] = await chrome.tabs.query({ 
        active: true, 
        currentWindow: true 
      })
      
      if (activeTab?.id) {
        await chrome.tabs.sendMessage(activeTab.id, {
          action: checked ? "showSidebar" : "hideSidebar"
        })
      }
    } catch (error) {
      console.error("[Popup] Failed to toggle sidebar:", error)
    }
  }

  /**
   * Initiates Google Sign In flow and enables sidebar on success
   */
  const handleSignIn = async () => {
    try {
      const response = await chrome.runtime.sendMessage({ action: "signIn" })
      if (response.success) {
        setUser(response.user)
        setIsSignedIn(true)
        await handleSidebarToggle(true)
      } else {
        console.error("[Popup] Sign in failed:", response.error)
      }
    } catch (error) {
      console.error("[Popup] Sign in error:", error)
    }
  }

  /**
   * Handles sign out and disables sidebar
   */
  const handleSignOut = async () => {
    try {
      await chrome.runtime.sendMessage({ action: "signOut" })
      setUser(null)
      setIsSignedIn(false)
      await handleSidebarToggle(false)
    } catch (error) {
      console.error("[Popup] Sign out error:", error)
    }
  }

  if (isLoading) {
    return (
      <div className="p-4 w-64 flex items-center justify-center">
        <span className="text-sm text-muted-foreground">Loading...</span>
      </div>
    )
  }

  return (
    <div className="p-4 w-64 space-y-4">
      <h1 className="text-lg font-bold">MBA Essay AI Assistant</h1>
      
      {isSignedIn && user ? (
        <div className="flex items-center space-x-3 p-2 border rounded-lg">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={handleSignOut}
          >
            Sign Out
          </Button>
        </div>
      ) : (
        <Button 
          className="w-full"
          onClick={handleSignIn}
        >
          Sign in with Google
        </Button>
      )}

      <div className="flex items-center space-x-2">
        <Switch 
          id="sidebar-toggle" 
          checked={isSidebarEnabled} 
          onCheckedChange={handleSidebarToggle}
        />
        <Label htmlFor="sidebar-toggle">Enable Sidebar</Label>
      </div>

      <p className="text-sm text-muted-foreground">
        {!isSignedIn 
          ? "Sign in to use the MBA Essay AI Assistant" 
          : isSidebarEnabled 
            ? "The sidebar will appear when you open Google Docs." 
            : "The sidebar is currently disabled."}
      </p>
    </div>
  )
}