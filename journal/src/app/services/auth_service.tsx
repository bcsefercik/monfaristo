export const authenticate = (email: string, password: string): any => {
  return {
    token:
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0cnlAdHJ5LmNvbSIsImlkIjoxLCJleHAiOjE3MDcwNzc5MTd9.u_PvPvlzd_csRyXCK3bguprlPVpEK5Ung7h7JQ_zT-8",
    user: {
      email,
      password,
    },
  };
};
