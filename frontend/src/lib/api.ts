const API_BASE_URL = 'http://localhost:8000'

export interface Alert {
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

export interface User {
  id: number
  name: string
  email: string
  is_admin: boolean
  team_name?: string
}

export interface Team {
  id: number
  name: string
}

export interface Analytics {
  total_alerts: number
  active_alerts: number
  total_deliveries: number
  read_count: number
  snoozed_count: number
  severity_breakdown: {
    Info: number
    Warning: number
    Critical: number
  }
}

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // User endpoints
  async getUsers(): Promise<User[]> {
    return this.request<User[]>('/users')
  }

  async getTeams(): Promise<Team[]> {
    return this.request<Team[]>('/teams')
  }

  async getUserAlerts(userId: number): Promise<Alert[]> {
    return this.request<Alert[]>(`/users/${userId}/alerts`)
  }

  async snoozeAlert(userId: number, alertId: number): Promise<void> {
    await this.request(`/users/${userId}/alerts/${alertId}/snooze`, {
      method: 'POST',
    })
  }

  async markAlertRead(userId: number, alertId: number): Promise<void> {
    await this.request(`/users/${userId}/alerts/${alertId}/read`, {
      method: 'POST',
    })
  }

  async markAlertUnread(userId: number, alertId: number): Promise<void> {
    await this.request(`/users/${userId}/alerts/${alertId}/unread`, {
      method: 'POST',
    })
  }

  // Admin endpoints
  async createAlert(alertData: any): Promise<{ id: number; message: string }> {
    return this.request('/admin/alerts', {
      method: 'POST',
      body: JSON.stringify(alertData),
    })
  }

  async getAllAlerts(): Promise<Alert[]> {
    return this.request<Alert[]>('/admin/alerts')
  }

  async toggleAlert(alertId: number): Promise<{ message: string }> {
    return this.request(`/admin/alerts/${alertId}/toggle`, {
      method: 'PUT',
    })
  }

  async triggerReminders(): Promise<{ message: string }> {
    return this.request('/admin/trigger-reminders', {
      method: 'POST',
    })
  }

  // User & Team Management
  async createUser(userData: any): Promise<User> {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async updateUser(userId: number, userData: any): Promise<User> {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    })
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    return this.request(`/users/${userId}`, {
      method: 'DELETE',
    })
  }

  async createTeam(teamData: any): Promise<Team> {
    return this.request('/teams', {
      method: 'POST',
      body: JSON.stringify(teamData),
    })
  }

  async updateTeam(teamId: number, teamData: any): Promise<Team> {
    return this.request(`/teams/${teamId}`, {
      method: 'PUT',
      body: JSON.stringify(teamData),
    })
  }

  async deleteTeam(teamId: number): Promise<{ message: string }> {
    return this.request(`/teams/${teamId}`, {
      method: 'DELETE',
    })
  }

  // Analytics
  async getAnalytics(): Promise<Analytics> {
    return this.request<Analytics>('/analytics')
  }
}

export const apiClient = new ApiClient()