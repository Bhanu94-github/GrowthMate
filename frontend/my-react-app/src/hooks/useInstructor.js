import { useQuery } from '@tanstack/react-query';
import { getInstructorDashboardData } from '../api/api';
import toast from 'react-hot-toast';

export function useInstructor() {
  const { data: instructorData, isLoading, error } = useQuery({
    queryKey: ['instructorDashboard'],
    queryFn: getInstructorDashboardData,
    onError: (error) => {
      toast.error(error.message || 'Failed to fetch instructor data');
    },
  });

  return {
    instructorData,
    isLoading,
    error,
  };
}</brtAction>