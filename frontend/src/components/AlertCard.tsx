'use client'

import { useState } from 'react'
import { Clock, Eye, EyeOff, Pause, AlertTriangle, Info, AlertCircle } from 'lucide-react'

interface Alert {
  id: number
  title: string
  message: string
  severity: 'Info' | 'Warning' | 'Critical'
  visibility_type: string
  is_active: boolean
  created_at: string
  is_read: boolean
  is_snoozed: boolean
}

interface AlertCardProps {
  alert: Alert
  onSnooze: (id: number) => void
  onMarkRead: (id: number) => void
}

export default function AlertCard({ alert, onSnooze, onMarkRead }: AlertCardProps) {
  const [isAnimating, setIsAnimating] = useState(false)

  const getSeverityIcon = () => {
    switch (alert.severity) {
      case 'Info':
        return <Info className="w-5 h-5 text-blue-500" />
      case 'Warning':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />
      case 'Critical':
        return <AlertCircle className="w-5 h-5 text-red-500" />
    }
  }

  const getSeverityClass = () => {
    switch (alert.severity) {
      case 'Info':
        return 'alert-info'
      case 'Warning':
        return 'alert-warning'
      case 'Critical':
        return 'alert-critical'
    }
  }

  const handleAction = (action: () => void) => {
    setIsAnimating(true)
    setTimeout(() => {
      action()
      setIsAnimating(false)
    }, 200)
  }

  return (
    <div className={`card hover:shadow-md transition-all duration-300 ${isAnimating ? 'scale-95' : 'scale-100'} ${
      alert.severity === 'Critical' && !alert.is_read ? 'animate-pulse-soft' : ''
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {getSeverityIcon()}
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {alert.title}
              </h3>
              {!alert.is_read && (
                <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
              )}
            </div>
            <p className="text-gray-600 dark:text-gray-300 mb-3">
              {alert.message}
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityClass()}`}>
                {alert.severity}
              </span>
              <span className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{new Date(alert.created_at).toLocaleDateString()}</span>
              </span>
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-xs">
                {alert.visibility_type}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2 ml-4">
          {alert.is_snoozed && (
            <span className="flex items-center space-x-1 text-xs text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 px-2 py-1 rounded-full">
              <Pause className="w-3 h-3" />
              <span>Snoozed</span>
            </span>
          )}
          
          <button
            onClick={() => handleAction(() => onMarkRead(alert.id))}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              alert.is_read
                ? 'text-gray-400 dark:text-gray-500'
                : 'text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20'
            }`}
            title={alert.is_read ? 'Mark as unread' : 'Mark as read'}
          >
            {alert.is_read ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
          
          {!alert.is_snoozed && (
            <button
              onClick={() => handleAction(() => onSnooze(alert.id))}
              className="p-2 rounded-lg text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors duration-200"
              title="Snooze for 24 hours"
            >
              <Pause className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}