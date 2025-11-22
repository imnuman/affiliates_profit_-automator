import { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import { useUIStore } from '../../store/uiStore'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const sidebarOpen = useUIStore(state => state.sidebarOpen)

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:pl-64' : 'lg:pl-0'}`}>
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
