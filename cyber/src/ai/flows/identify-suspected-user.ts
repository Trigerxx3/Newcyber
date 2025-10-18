'use server';
/**
 * @fileOverview Performs OSINT-like analysis on a given username to identify potential linked profiles and assess risk.
 *
 * - identifySuspectedUser - A function that handles the user identification process.
 * - IdentifySuspectedUserInput - The input type for the identifySuspectedUser function.
 * - IdentifySuspectedUserOutput - The return type for the identifySuspectedUser function.
 */

import { z } from 'genkit';

const IdentifySuspectedUserInputSchema = z.object({
  username: z.string().describe('The username to investigate.'),
  platform: z
    .enum(['Telegram', 'WhatsApp', 'Instagram'])
    .describe('The social media platform the username is from.'),
});
export type IdentifySuspectedUserInput = z.infer<typeof IdentifySuspectedUserInputSchema>;

const IdentifySuspectedUserOutputSchema = z.object({
  username: z.string(),
  platform: z.string(),
  linkedProfiles: z.array(z.string()).describe('Linked profiles found across platforms'),
  email: z.string().nullable().describe('Potential email address'),
  riskLevel: z.enum(['Low', 'Medium', 'High', 'Critical']),
  summary: z.string().describe('Summary of investigation findings'),
  toolsUsed: z.array(z.string()).describe('OSINT tools used in investigation'),
  totalProfilesFound: z.number().describe('Total number of profiles found'),
  confidenceLevel: z.enum(['low', 'medium', 'high']).describe('Confidence in results'),
});
export type IdentifySuspectedUserOutput = z.infer<typeof IdentifySuspectedUserOutputSchema>;

export async function identifySuspectedUser(input: IdentifySuspectedUserInput): Promise<IdentifySuspectedUserOutput> {
  try {
    // Call Flask backend with real OSINT tools
    const response = await fetch('http://localhost:5000/api/osint/investigate-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: input.username,
        platform: input.platform,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Investigation failed');
    }
    
  } catch (error) {
    console.error('OSINT investigation failed:', error);
    
    // Fallback to mock data if real tools fail
    return {
      username: input.username,
      platform: input.platform,
      linkedProfiles: [],
      email: null,
      riskLevel: 'Low',
      summary: `Investigation failed: ${error}. Please ensure OSINT tools are installed.`,
      toolsUsed: [],
      totalProfilesFound: 0,
      confidenceLevel: 'low',
    };
  }
}
