import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/auth'
import { useAuthStore } from '../store/authStore'
import type { LoginCredentials, SignupData } from '../services/types'

export function useAuth() {
  const navigate = useNavigate()
  const { setUser, setTokens, logout: logoutStore } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: async data => {
      setTokens(data.access_token, data.refresh_token)
      // Fetch user data
      const user = await authService.getCurrentUser()
      setUser(user)
      navigate('/dashboard')
    },
  })

  const signupMutation = useMutation({
    mutationFn: authService.signup,
    onSuccess: async (user, variables) => {
      // Auto-login after signup
      const authData = await authService.login({
        email: variables.email,
        password: variables.password,
      })
      setTokens(authData.access_token, authData.refresh_token)
      setUser(user)
      navigate('/dashboard')
    },
  })

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      logoutStore()
      navigate('/login')
    },
  })

  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authService.getCurrentUser,
    enabled: useAuthStore.getState().isAuthenticated,
    staleTime: Infinity,
  })

  return {
    login: loginMutation.mutate,
    signup: signupMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isSigningUp: signupMutation.isPending,
    loginError: loginMutation.error,
    signupError: signupMutation.error,
    currentUser,
    isLoadingUser,
  }
}
