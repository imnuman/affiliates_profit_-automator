import { Menu, Bell, User } from 'lucide-react'
import { Button } from '../ui/button'
import { useUIStore } from '../../store/uiStore'
import { useAuthStore } from '../../store/authStore'
import { useAuth } from '../../hooks/useAuth'

export default function Header() {
  const toggleSidebar = useUIStore(state => state.toggleSidebar)
  const user = useAuthStore(state => state.user)
  const { logout } = useAuth()

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center gap-4 px-6">
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="lg:hidden">
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex-1" />

        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <User className="h-4 w-4" />
          </div>
          <div className="hidden text-sm md:block">
            <div className="font-medium">{user?.full_name || user?.email}</div>
            <div className="text-xs text-muted-foreground capitalize">{user?.tier}</div>
          </div>
        </div>

        <Button variant="outline" size="sm" onClick={() => logout()}>
          Logout
        </Button>
      </div>
    </header>
  )
}
