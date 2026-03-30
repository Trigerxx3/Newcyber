// Sample data for development and testing
export const getSampleDashboardData = () => {
  return {
    flaggedPosts: [
      {
        id: 1,
        content: "Sample flagged post content",
        platform: "Instagram",
        username: "sample_user",
        timestamp: new Date().toISOString(),
        riskScore: 85,
        flaggedKeywords: ["drug", "sale"]
      }
    ],
    suspectedUsers: [
      {
        id: 1,
        username: "sample_user",
        platform: "Instagram",
        riskScore: 75,
        lastActivity: new Date().toISOString(),
        flaggedContent: 3
      }
    ],
    analysisResults: [
      {
        id: 1,
        content: "Sample analysis result",
        riskLevel: "High" as const,
        score: 90,
        reasons: ["Contains drug-related keywords", "High risk language"],
        timestamp: new Date().toISOString()
      }
    ]
  }
}
