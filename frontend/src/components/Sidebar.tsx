'use client'

import { useState } from 'react'
import { Bell, Settings, BarChart3, Users, Shield, Moon, Sun } from 'lucide-react'

interface SidebarProps {
  currentView: string
  onViewChange: (view: string) => void
  isAdmin: boolean
}

export default function Sidebar({ currentView, onViewChange, isAdmin }: SidebarProps) {
  const [isDark, setIsDark] = useState(false)

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  const menuItems = [
    { id: 'alerts', label: 'My Alerts', icon: Bell, adminOnly: false },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, adminOnly: false },
    ...(isAdmin ? [
      { id: 'admin-alerts', label: 'Manage Alerts', icon: Shield, adminOnly: true },
      { id: 'users', label: 'Users & Teams', icon: Users, adminOnly: true },
    ] : [])
  ]

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-screen flex flex-col">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
          Alert Platform
        </h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
              currentView === item.id
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span className="font-medium">{isDark ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>
    </div>
  )
}