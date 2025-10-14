import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/contexts/AuthContext'
import { AlertCircle, Loader2 } from 'lucide-react'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, register } = useAuth()
  const [isSignUp, setIsSignUp] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      if (isSignUp) {
        // Sign up
        if (formData.password !== formData.password_confirm) {
          setError("Passwords don't match")
          setIsLoading(false)
          return
        }

        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password_confirm,
          first_name: formData.first_name,
          last_name: formData.last_name,
        })

        onClose()
      } else {
        // Sign in
        await login(formData.username, formData.password)
        onClose()
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 
                          err.response?.data?.error ||
                          Object.values(err.response?.data || {}).flat().join(', ') ||
                          'Authentication failed. Please try again.'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleMode = () => {
    setIsSignUp(!isSignUp)
    setError(null)
    setFormData({
      username: '',
      email: '',
      password: '',
      password_confirm: '',
      first_name: '',
      last_name: '',
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isSignUp ? 'Create an Account' : 'Sign In'}</DialogTitle>
          <DialogDescription>
            {isSignUp 
              ? 'Create a new account to start analyzing news articles'
              : 'Sign in to access your analysis history'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {error && (
            <div className="flex items-center gap-2 text-destructive bg-destructive/10 p-3 rounded-md">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="username" className="text-sm font-medium">
              Username
            </label>
            <Input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleInputChange}
              required
              disabled={isLoading}
              placeholder="Enter your username"
            />
          </div>

          {isSignUp && (
            <>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={isLoading}
                  placeholder="your.email@example.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="first_name" className="text-sm font-medium">
                    First Name
                  </label>
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    placeholder="John"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="last_name" className="text-sm font-medium">
                    Last Name
                  </label>
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    disabled={isLoading}
                    placeholder="Doe"
                  />
                </div>
              </div>
            </>
          )}

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading}
              placeholder="Enter your password"
            />
          </div>

          {isSignUp && (
            <div className="space-y-2">
              <label htmlFor="password_confirm" className="text-sm font-medium">
                Confirm Password
              </label>
              <Input
                id="password_confirm"
                name="password_confirm"
                type="password"
                value={formData.password_confirm}
                onChange={handleInputChange}
                required
                disabled={isLoading}
                placeholder="Confirm your password"
              />
            </div>
          )}

          <div className="flex flex-col gap-2 pt-4">
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isSignUp ? 'Creating Account...' : 'Signing In...'}
                </>
              ) : (
                isSignUp ? 'Sign Up' : 'Sign In'
              )}
            </Button>

            <Button
              type="button"
              variant="ghost"
              onClick={toggleMode}
              disabled={isLoading}
              className="w-full"
            >
              {isSignUp 
                ? 'Already have an account? Sign in' 
                : "Don't have an account? Sign up"
              }
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default AuthModal
