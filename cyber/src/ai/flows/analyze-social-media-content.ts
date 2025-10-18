// This file is machine-generated - edit with care!

'use server';

/**
 * @fileOverview Analyzes social media content (text and images) to identify potential drug trafficking indicators using GenAI.
 *
 * - analyzeSocialMediaContent - A function that handles the analysis of social media content.
 * - AnalyzeSocialMediaContentInput - The input type for the analyzeSocialMediaContent function.
 * - AnalyzeSocialMediaContentOutput - The return type for the analyzeSocialMediaContent function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AnalyzeSocialMediaContentInputSchema = z.object({
  platform: z
    .enum(['Telegram', 'WhatsApp', 'Instagram'])
    .describe('The social media platform the content is from.'),
  content: z.string().describe('The text content to analyze.'),
  image: z
    .string()
    .optional()
    .describe(
      'An optional image associated with the content, as a data URI that must include a MIME type and use Base64 encoding. Expected format: \'data:<mimetype>;base64,<encoded_data>\'.' /* data-uri */
    ),
});
export type AnalyzeSocialMediaContentInput = z.infer<typeof AnalyzeSocialMediaContentInputSchema>;

const AnalyzeSocialMediaContentOutputSchema = z.object({
  indicators: z
    .array(z.string())
    .describe('A list of potential drug trafficking indicators found in the content.'),
  riskLevel: z
    .enum(['Low', 'Medium', 'High'])
    .describe('The overall risk level associated with the content.'),
  reasoning: z.string().describe('The reasoning behind the identified indicators and risk level.'),
  matchedKeywords: z.array(z.string()).describe('A list of specific keywords related to drugs found in the content.'),
  matchedEmojis: z.array(z.string()).describe('A list of emojis related to drugs found in the content.'),
});
export type AnalyzeSocialMediaContentOutput = z.infer<typeof AnalyzeSocialMediaContentOutputSchema>;

export async function analyzeSocialMediaContent(
  input: AnalyzeSocialMediaContentInput
): Promise<AnalyzeSocialMediaContentOutput> {
  return analyzeSocialMediaContentFlow(input);
}

const analyzeSocialMediaContentPrompt = ai.definePrompt({
  name: 'analyzeSocialMediaContentPrompt',
  input: {schema: AnalyzeSocialMediaContentInputSchema},
  output: {schema: AnalyzeSocialMediaContentOutputSchema},
  prompt: `You are an AI assistant specializing in identifying drug trafficking activities on social media platforms.

  Analyze the content from {{platform}} provided below. Identify any potential indicators of drug trafficking, including specific keywords and emojis.
  Assess the overall risk level (Low, Medium, or High) based on the identified indicators.
  Provide a clear explanation of your reasoning for the identified indicators and the assigned risk level.
  Extract the specific drug-related keywords and emojis into the 'matchedKeywords' and 'matchedEmojis' fields respectively.

  Content: {{{content}}}
  {{#if image}}
  Image: {{media url=image}}
  {{/if}}
  \n  Format your output as a valid JSON object of AnalyzeSocialMediaContentOutputSchema schema. Pay attention to data types.
  Do not include any introductory or explanatory text outside of the JSON object.
  `,
});

const analyzeSocialMediaContentFlow = ai.defineFlow(
  {
    name: 'analyzeSocialMediaContentFlow',
    inputSchema: AnalyzeSocialMediaContentInputSchema,
    outputSchema: AnalyzeSocialMediaContentOutputSchema,
  },
  async input => {
    const {output} = await analyzeSocialMediaContentPrompt(input);
    return output!;
  }
);
