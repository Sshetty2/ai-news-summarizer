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
        <div className="container flex h-16 items-center">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="mr-2 md:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Logo */}
          <div className="mr-6 flex items-center space-x-2">
            <Newspaper className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">News Analyzer</span>
          </div>

          {/* Search bar */}
          <div className="flex flex-1 items-center space-x-2 md:mr-6">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-2">
            {user ? (
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">
                  <User className="h-3 w-3 mr-1" />
                  {user.username}
                </Badge>
                <Button variant="ghost" size="icon" onClick={onLogout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <Button variant="outline" onClick={onSignIn}>
                Sign In
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <aside className={`
          fixed inset-y-0 z-40 w-64 transform bg-background border-r transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:static md:inset-0
        `}>
          <div className="flex h-full flex-col">
            <div className="flex-1 px-3 py-4">
              <nav className="space-y-2">
                <Button variant="ghost" className="w-full justify-start">
                  <Home className="mr-2 h-4 w-4" />
                  Dashboard
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  <Newspaper className="mr-2 h-4 w-4" />
                  Latest News
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Trending
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  My Analysis
                </Button>
                <Button variant="ghost" className="w-full justify-start">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Button>
              </nav>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 md:ml-0">
          {children ? (
            <div className="container py-6">
              {children}
            </div>
          ) : (
            <div className="grid lg:grid-cols-2 gap-6 p-6">
              {/* Left Panel - News Articles */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">Latest News</h2>
                  <Button variant="outline" size="sm">
                    Refresh
                  </Button>
                </div>
                <Card className="p-6">
                  {leftPanel || (
                    <div className="text-center text-muted-foreground py-12">
                      <Newspaper className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>News articles will appear here</p>
                    </div>
                  )}
                </Card>
              </div>

              {/* Right Panel - Analysis Dashboard */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">Analysis Dashboard</h2>
                  <Button variant="outline" size="sm">
                    <BarChart3 className="h-4 w-4 mr-1" />
                    View All
                  </Button>
                </div>
                <Card className="p-6">
                  {rightPanel || (
                    <div className="text-center text-muted-foreground py-12">
                      <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Click on an article to see analysis</p>
                    </div>
                  )}
                </Card>
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
