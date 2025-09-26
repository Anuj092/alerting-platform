'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import AlertCard from '@/components/AlertCard'
import CreateAlertModal from '@/components/CreateAlertModal'
import UserModal from '@/components/UserModal'
import TeamModal from '@/components/TeamModal'
import { apiClient, Alert, User, Team, Analytics } from '@/lib/api'
import { Plus, Filter, Search, BarChart3, Users, AlertTriangle, CheckCircle, Clock, Pause, Edit, Trash2 } from 'lucide-react'

export default function Home() {
  const [currentView, setCurrentView] = useState('alerts')
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [allAlerts, setAllAlerts] = useState<Alert[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isUserModalOpen, setIsUserModalOpen] = useState(false)
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [editingTeam, setEditingTeam] = useState<Team | null>(null)
  const [filterSeverity, setFilterSeverity] = useState('All')
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (currentUser) {
      if (currentView === 'alerts') {
        loadUserAlerts()
      } else if (currentView === 'admin-alerts') {
        loadAllAlerts()
      } else if (currentView === 'analytics') {
        loadAnalytics()
      }
    }
  }, [currentView, currentUser])

  const loadInitialData = async () => {
    try {
      const [usersData, teamsData] = await Promise.all([
        apiClient.getUsers(),
        apiClient.getTeams()
      ])
      setUsers(usersData)
      setTeams(teamsData)
      
      // Set first admin user as current user for demo
      const adminUser = usersData.find(u => u.is_admin) || usersData[0]
      setCurrentUser(adminUser)
    } catch (error) {
      console.error('Failed to load initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadUserAlerts = async () => {
    if (!currentUser) return
    try {
      const alertsData = await apiClient.getUserAlerts(currentUser.id)
      setAlerts(alertsData)
    } catch (error) {
      console.error('Failed to load alerts:', error)
    }
  }

  const loadAllAlerts = async () => {
    try {
      const alertsData = await apiClient.getAllAlerts()
      setAllAlerts(alertsData)
    } catch (error) {
      console.error('Failed to load all alerts:', error)
    }
  }

  const loadAnalytics = async () => {
    try {
      const analyticsData = await apiClient.getAnalytics()
      setAnalytics(analyticsData)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    }
  }

  const handleSnoozeAlert = async (alertId: number) => {
    if (!currentUser) return
    try {
      await apiClient.snoozeAlert(currentUser.id, alertId)
      loadUserAlerts()
    } catch (error) {
      console.error('Failed to snooze alert:', error)
    }
  }

  const handleMarkRead = async (alertId: number) => {
    if (!currentUser) return
    try {
      const alert = alerts.find(a => a.id === alertId)
      if (alert?.is_read) {
        await apiClient.markAlertUnread(currentUser.id, alertId)
      } else {
        await apiClient.markAlertRead(currentUser.id, alertId)
      }
      loadUserAlerts()
    } catch (error) {
      console.error('Failed to toggle alert read status:', error)
    }
  }

  const handleCreateAlert = async (alertData: any) => {
    try {
      await apiClient.createAlert(alertData)
      setIsCreateModalOpen(false)
      loadAllAlerts()
    } catch (error) {
      console.error('Failed to create alert:', error)
    }
  }

  const handleToggleAlert = async (alertId: number) => {
    try {
      await apiClient.toggleAlert(alertId)
      loadAllAlerts()
    } catch (error) {
      console.error('Failed to toggle alert:', error)
    }
  }

  const handleUserSubmit = async (userData: any) => {
    try {
      if (editingUser) {
        await apiClient.updateUser(editingUser.id, userData)
      } else {
        await apiClient.createUser(userData)
      }
      setIsUserModalOpen(false)
      setEditingUser(null)
      loadInitialData()
    } catch (error) {
      console.error('Failed to save user:', error)
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (confirm('Are you sure you want to delete this user?')) {
      try {
        await apiClient.deleteUser(userId)
        loadInitialData()
      } catch (error) {
        console.error('Failed to delete user:', error)
      }
    }
  }

  const handleTeamSubmit = async (teamData: any) => {
    try {
      if (editingTeam) {
        await apiClient.updateTeam(editingTeam.id, teamData)
      } else {
        await apiClient.createTeam(teamData)
      }
      setIsTeamModalOpen(false)
      setEditingTeam(null)
      loadInitialData()
    } catch (error) {
      console.error('Failed to save team:', error)
    }
  }

  const handleDeleteTeam = async (teamId: number) => {
    if (confirm('Are you sure you want to delete this team?')) {
      try {
        await apiClient.deleteTeam(teamId)
        loadInitialData()
      } catch (error) {
        console.error('Failed to delete team:', error)
      }
    }
  }

  const filteredAlerts = alerts.filter(alert => {
    const matchesSeverity = filterSeverity === 'All' || alert.severity === filterSeverity
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.message.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSeverity && matchesSearch
  })

  const filteredAllAlerts = allAlerts.filter(alert => {
    const matchesSeverity = filterSeverity === 'All' || alert.severity === filterSeverity
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.message.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSeverity && matchesSearch
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar 
        currentView={currentView} 
        onViewChange={setCurrentView}
        isAdmin={currentUser?.is_admin || false}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {currentView === 'alerts' && 'My Alerts'}
                {currentView === 'admin-alerts' && 'Manage Alerts'}
                {currentView === 'analytics' && 'Analytics Dashboard'}
                {currentView === 'users' && 'Users & Teams'}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Welcome back, {currentUser?.name}
              </p>
            </div>
            
            {currentView === 'admin-alerts' && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Create Alert</span>
              </button>
            )}
            
            {currentView === 'users' && (
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setEditingUser(null)
                    setIsUserModalOpen(true)
                  }}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add User</span>
                </button>
                <button
                  onClick={() => {
                    setEditingTeam(null)
                    setIsTeamModalOpen(true)
                  }}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Team</span>
                </button>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          {(currentView === 'alerts' || currentView === 'admin-alerts') && (
            <>
              <div className="flex items-center space-x-4 mb-6">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search alerts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  />
                </div>
                
                <select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="All">All Severities</option>
                  <option value="Info">Info</option>
                  <option value="Warning">Warning</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>

              <div className="space-y-4">
                {currentView === 'alerts' && filteredAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    onSnooze={handleSnoozeAlert}
                    onMarkRead={handleMarkRead}
                  />
                ))}
                
                {currentView === 'admin-alerts' && (
                  <div className="grid gap-4">
                    {filteredAllAlerts.map((alert) => (
                      <div key={alert.id} className="card">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                              {alert.title}
                            </h3>
                            <p className="text-gray-600 dark:text-gray-300 mb-3">
                              {alert.message}
                            </p>
                            <div className="flex items-center space-x-4 text-sm">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                alert.severity === 'Info' ? 'alert-info' :
                                alert.severity === 'Warning' ? 'alert-warning' : 'alert-critical'
                              }`}>
                                {alert.severity}
                              </span>
                              <span>{alert.visibility_type}</span>
                              <span>{new Date(alert.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <button
                            onClick={() => handleToggleAlert(alert.id)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                              alert.is_active
                                ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/20 dark:text-red-400'
                                : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/20 dark:text-green-400'
                            }`}
                          >
                            {alert.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {currentView === 'analytics' && analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Alerts</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.total_alerts}</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-primary-600" />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Alerts</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.active_alerts}</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-orange-600" />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Read Alerts</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.read_count}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Snoozed</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.snoozed_count}</p>
                  </div>
                  <Pause className="w-8 h-8 text-purple-600" />
                </div>
              </div>
            </div>
          )}

          {currentView === 'users' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Users</h3>
                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{user.name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{user.email}</p>
                        {user.team_name && (
                          <p className="text-xs text-gray-500 dark:text-gray-500">{user.team_name}</p>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {user.is_admin && (
                          <span className="px-2 py-1 bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400 text-xs rounded-full">
                            Admin
                          </span>
                        )}
                        <button
                          onClick={() => {
                            setEditingUser(user)
                            setIsUserModalOpen(true)
                          }}
                          className="p-1 text-gray-400 hover:text-primary-600"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="p-1 text-gray-400 hover:text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Teams</h3>
                <div className="space-y-3">
                  {teams.map((team) => (
                    <div key={team.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{team.name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {users.filter(u => u.team_name === team.name).length} members
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setEditingTeam(team)
                            setIsTeamModalOpen(true)
                          }}
                          className="p-1 text-gray-400 hover:text-primary-600"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteTeam(team.id)}
                          className="p-1 text-gray-400 hover:text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      <CreateAlertModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateAlert}
        teams={teams}
        users={users}
      />
      
      <UserModal
        isOpen={isUserModalOpen}
        onClose={() => {
          setIsUserModalOpen(false)
          setEditingUser(null)
        }}
        onSubmit={handleUserSubmit}
        user={editingUser}
        teams={teams}
      />
      
      <TeamModal
        isOpen={isTeamModalOpen}
        onClose={() => {
          setIsTeamModalOpen(false)
          setEditingTeam(null)
        }}
        onSubmit={handleTeamSubmit}
        team={editingTeam}
      />
    </div>
  )
}