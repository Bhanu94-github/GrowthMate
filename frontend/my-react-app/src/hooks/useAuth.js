import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { loginStudent, registerStudent } from '../api/api';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const loginMutation = useMutation({
    mutationFn: ({ username, password }) => loginStudent(username, password),
    onSuccess: (data) => {
      queryClient.setQueryData(['user'], data);
      toast.success('Successfully logged in!');
      navigate('/student/dashboard');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to login');
    },
  });

  const registerMutation = useMutation({
    mutationFn: (userData) => registerStudent(userData),
    onSuccess: () => {
      toast.success('Registration successful! Please check your email for verification.');
      navigate('/signin');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to register');
    },
  });

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    isLoading: loginMutation.isPending || registerMutation.isPending,
  };
}