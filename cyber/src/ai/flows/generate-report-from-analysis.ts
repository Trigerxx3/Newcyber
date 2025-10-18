// src/ai/flows/generate-report-from-analysis.ts
'use server';
/**
 * @fileOverview Generates a summary report based on content and risk analysis.
 *
 * - generateReportFromAnalysis - A function that generates a report based on analysis results.
 * - GenerateReportFromAnalysisInput - The input type for the generateReportFromAnalysis function.
 * - GenerateReportFromAnalysisOutput - The return type for the generateReportFromAnalysis function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateReportFromAnalysisInputSchema = z.object({
  contentAnalysis: z.string().describe('The analysis of the content.'),
  riskAssessment: z.string().describe('The risk assessment results.'),
});
export type GenerateReportFromAnalysisInput = z.infer<typeof GenerateReportFromAnalysisInputSchema>;

const GenerateReportFromAnalysisOutputSchema = z.object({
  report: z.string().describe('The generated summary report.'),
});
export type GenerateReportFromAnalysisOutput = z.infer<typeof GenerateReportFromAnalysisOutputSchema>;

export async function generateReportFromAnalysis(input: GenerateReportFromAnalysisInput): Promise<GenerateReportFromAnalysisOutput> {
  return generateReportFromAnalysisFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateReportFromAnalysisPrompt',
  input: {schema: GenerateReportFromAnalysisInputSchema},
  output: {schema: GenerateReportFromAnalysisOutputSchema},
  prompt: `You are an expert in generating summary reports based on content and risk analysis.

  Based on the content analysis and risk assessment provided, generate a comprehensive summary report highlighting key findings and potential risks.

  Content Analysis: {{{contentAnalysis}}}
  Risk Assessment: {{{riskAssessment}}}

  Report:
`,
});

const generateReportFromAnalysisFlow = ai.defineFlow(
  {
    name: 'generateReportFromAnalysisFlow',
    inputSchema: GenerateReportFromAnalysisInputSchema,
    outputSchema: GenerateReportFromAnalysisOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
