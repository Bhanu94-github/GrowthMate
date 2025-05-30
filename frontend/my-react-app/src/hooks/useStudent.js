import { useQuery } from '@tanstack/react-query';
import { getStudentDashboardData } from '../api/api';
import toast from 'react-hot-toast';

export function useStudent() {
  const { data: studentData, isLoading, error } = useQuery({
    queryKey: ['studentDashboard'],
    queryFn: getStudentDashboardData,
    onError: (error) => {
      toast.error(error.message || 'Failed to fetch student data');
    },
  });

  return {
    studentData,
    isLoading,
    error,
  };
}