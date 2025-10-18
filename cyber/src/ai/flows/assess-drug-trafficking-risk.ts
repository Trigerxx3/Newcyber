'use server';
/**
 * @fileOverview Assesses the likelihood of drug trafficking involvement based on content analysis.
 *
 * - assessDrugTraffickingRisk - A function that assesses the risk of drug trafficking.
 * - AssessDrugTraffickingRiskInput - The input type for the assessDrugTraffickingRisk function.
 * - AssessDrugTraffickingRiskOutput - The return type for the assessDrugTraffickingRisk function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AssessDrugTraffickingRiskInputSchema = z.object({
  contentAnalysis: z
    .string()
    .describe('The analyzed content from social media (Telegram, WhatsApp, Instagram).'),
});
export type AssessDrugTraffickingRiskInput = z.infer<typeof AssessDrugTraffickingRiskInputSchema>;

const AssessDrugTraffickingRiskOutputSchema = z.object({
  riskScore: z
    .number()
    .describe('A score from 0 to 100 representing the likelihood of drug trafficking involvement.'),
  riskLevel: z
    .enum(['Low', 'Medium', 'High'])
    .describe(
      'A qualitative assessment of the risk level (e.g., Low, Medium, High) based on the risk score.'
    ),
  indicators: z
    .array(z.string())
    .describe('Specific indicators from the content analysis that suggest drug trafficking.'),
});
export type AssessDrugTraffickingRiskOutput = z.infer<typeof AssessDrugTraffickingRiskOutputSchema>;

export async function assessDrugTraffickingRisk(
  input: AssessDrugTraffickingRiskInput
): Promise<AssessDrugTraffickingRiskOutput> {
  return assessDrugTraffickingRiskFlow(input);
}

const prompt = ai.definePrompt({
  name: 'assessDrugTraffickingRiskPrompt',
  input: {schema: AssessDrugTraffickingRiskInputSchema},
  output: {schema: AssessDrugTraffickingRiskOutputSchema},
  prompt: `You are an expert in identifying drug trafficking activities based on analyzed content from social media platforms.

  Given the following content analysis, assess the likelihood of drug trafficking involvement. Provide a risk score between 0 and 100, a qualitative risk level (Low, Medium, High), and specific indicators that suggest drug trafficking.

  Content Analysis:
  {{contentAnalysis}}

  Provide the output in JSON format.
  Ensure the riskScore is a number between 0 and 100.  Ensure the riskLevel is one of "Low", "Medium", or "High".  Ensure indicators is an array of strings.
  `,
});

const assessDrugTraffickingRiskFlow = ai.defineFlow(
  {
    name: 'assessDrugTraffickingRiskFlow',
    inputSchema: AssessDrugTraffickingRiskInputSchema,
    outputSchema: AssessDrugTraffickingRiskOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
