import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Menu, 
  Search, 
  User, 
  Settings, 
  BarChart3, 
  Newspaper, 
  TrendingUp,
  LogOut,
  Home
} from 'lucide-react'

interface MainLayoutProps {
  children?: React.ReactNode
  leftPanel?: React.ReactNode
  rightPanel?: React.ReactNode
  user?: {
    username: string
    profile?: {
      avatar?: string
    }
  }
  onLogout?: () => void
  onSignIn?: () => void
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  leftPanel,
  rightPanel,
  user,
  onLogout,
  onSignIn
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center px-4 gap-4">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden flex-shrink-0"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Logo */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Newspaper className="h-5 w-5 text-primary" />
            <span className="text-lg font-bold">News Analyzer</span>
          </div>

          {/* Search bar - hidden on mobile */}
          <div className="hidden md:flex flex-1 max-w-md items-center ml-auto">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-9"
              />
            </div>
          </div>

          {/* Spacer */}
          <div className="flex-1 md:flex-none" />

          {/* User menu */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {user ? (
              <>
                <Badge variant="secondary" className="hidden sm:flex items-center h-9 px-3">
                  <User className="h-4 w-4 mr-1.5" />
                  {user.username}
                </Badge>
                <Button variant="ghost" size="icon" onClick={onLogout} className="h-9 w-9">
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <Button variant="outline" onClick={onSignIn} className="h-9">
                Sign In
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <aside className={`
          fixed inset-y-0 z-40 w-56 transform bg-background border-r transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:static md:inset-0
        `}>
          <div className="flex h-full flex-col pt-4">
            <div className="flex-1 px-2">
              <nav className="space-y-1">
                <Button variant="ghost" className="w-full justify-start h-9 text-sm">
                  <Home className="mr-2 h-4 w-4" />
                  Dashboard
                </Button>
                <Button variant="ghost" className="w-full justify-start h-9 text-sm">
                  <Newspaper className="mr-2 h-4 w-4" />
                  Latest News
                </Button>
                <Button variant="ghost" className="w-full justify-start h-9 text-sm">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Trending
                </Button>
                <Button variant="ghost" className="w-full justify-start h-9 text-sm">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  My Analysis
                </Button>
                <Button variant="ghost" className="w-full justify-start h-9 text-sm">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Button>
              </nav>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 md:ml-0 overflow-hidden">
          {children ? (
            <div className="container py-6">
              {children}
            </div>
          ) : (
            <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
              {/* Left Panel - News Articles (62% width) */}
              <div className="w-[62%] flex flex-col p-4 overflow-hidden">
                <div className="flex items-center justify-between pb-4">
                  <h2 className="text-xl font-bold">Latest News</h2>
                </div>
                <div className="flex-1 overflow-y-auto">
                  {leftPanel || (
                    <div className="text-center text-muted-foreground py-12">
                      <Newspaper className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>News articles will appear here</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Panel - Analysis Dashboard (38% width) */}
              <div className="w-[38%] flex flex-col border-l p-4 overflow-hidden">
                <div className="flex items-center justify-between pb-4">
                  <h2 className="text-xl font-bold">Analysis</h2>
                </div>
                <div className="flex-1 overflow-y-auto pr-1">
                  {rightPanel || (
                    <div className="text-center text-muted-foreground py-12">
                      <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Click on an article to see analysis</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default MainLayout
