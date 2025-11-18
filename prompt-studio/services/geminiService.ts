import { GoogleGenAI, Type, Modality } from "@google/genai";
import { Prompt, PromptType, GeminiContent } from "../types";

// FIX: Initialize the GoogleGenAI client. The API key must be sourced from process.env.API_KEY.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

/**
 * Enhances a given prompt using AI.
 * @param prompt The user's prompt.
 * @param type The type of prompt.
 * @returns An object with improvements and suggested tags, or a specific error object on failure.
 */
// Update: Removed `| null` from return type as it's never null.
export const getPromptEnhancements = async (prompt: string, type: PromptType): Promise<{ improvements: string; tags: string[] }> => {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `Analyze and enhance the following prompt for a ${type} generation AI. Provide a better, more detailed version and suggest 3-5 relevant tags. Prompt: "${prompt}"`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            improvements: {
              type: Type.STRING,
              description: 'The improved and enhanced prompt.'
            },
            tags: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: 'An array of 3 to 5 suggested tags.'
            }
          },
          required: ['improvements', 'tags']
        },
      },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Error enhancing prompt:", error);
    // FIX: Return a specific error object for the UI to handle.
    return { improvements: "AI analysis failed.", tags: [] };
  }
};

/**
 * Generates relevant tags in English and Persian for a given prompt.
 * @param prompt The user's prompt content.
 * @param type The type of prompt.
 * @returns An object with english_tags and persian_tags arrays, or a specific error object on failure.
 */
export const generateTags = async (prompt: string, type: PromptType): Promise<{ english_tags: string[]; persian_tags: string[] }> => {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `Analyze the following prompt for a ${type} generation AI. Generate 3-5 relevant tags in both English and Persian. The English tags should be lowercase, single-word or hyphenated, and suitable for searching. The Persian tags should be meaningful. Prompt: "${prompt}"`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            english_tags: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: 'An array of 3 to 5 relevant tags in English.'
            },
            persian_tags: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: 'An array of 3 to 5 relevant tags in Persian.'
            }
          },
          required: ['english_tags', 'persian_tags']
        },
      },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Error generating tags:", error);
    return { english_tags: [], persian_tags: [] };
  }
};

/**
 * Parses a natural language query into structured search filters using AI.
 * @param query The natural language search query from the user.
 * @returns An object with keywords, tags, rating filter, and sort option.
 */
export const getSemanticSearchFilters = async (query: string): Promise<{ keywords: string; tags: string[]; ratingFilter: number; sortOption: string; }> => {
  const prompt = `Analyze the user's search query for a "Prompt Studio" app. Extract relevant keywords, tags, rating filters, and a sort option.
  Query: "${query}"

  Rules:
  - 'keywords': A string of keywords to search for.
  - 'tags': An array of tags. Extract things that look like categories or specific attributes.
  - 'ratingFilter': A number. 0 for all, -1 for unrated, 3 for 3+, 4 for 4+, 5 for 5 stars. Infer from words like "best", "top-rated" (rating >= 4), "unrated", or "x stars". Default to 0.
  - 'sortOption': A string. Options are 'updatedAt-desc' (latest), 'updatedAt-asc' (oldest), 'rating-desc' (best), 'rating-asc' (worst), 'title-asc', 'title-desc'. Infer from words like "latest", "newest", "best", "top". Default to 'updatedAt-desc'.
  
  Return a valid JSON object.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            keywords: { type: Type.STRING },
            tags: { type: Type.ARRAY, items: { type: Type.STRING } },
            ratingFilter: { type: Type.NUMBER },
            sortOption: { type: Type.STRING },
          },
          required: ['keywords', 'tags', 'ratingFilter', 'sortOption']
        },
      },
    });

    const jsonText = response.text.trim();
    const parsed = JSON.parse(jsonText);
    const validSortOptions = ['updatedAt-desc', 'updatedAt-asc', 'rating-desc', 'rating-asc', 'title-asc', 'title-desc'];
    if (!validSortOptions.includes(parsed.sortOption)) {
      parsed.sortOption = 'updatedAt-desc'; // Default fallback
    }
    return parsed;

  } catch (error) {
    console.error("Error in semantic search:", error);
    return { keywords: query, tags: [], ratingFilter: 0, sortOption: 'updatedAt-desc' };
  }
};


/**
 * Generates an image from a text prompt.
 * @param prompt The text prompt for image generation.
 * @param aspectRatio The desired aspect ratio for the image.
 * @returns A base64 encoded image string, or null on failure.
 */
export const generateImage = async (prompt: string, aspectRatio: '1:1' | '16:9' | '9:16' | '4:3' | '3:4' = '1:1'): Promise<string | null> => {
  try {
    const response = await ai.models.generateImages({
      model: 'imagen-4.0-generate-001',
      prompt: prompt,
      config: {
        numberOfImages: 1,
        outputMimeType: 'image/png',
        aspectRatio: aspectRatio,
      },
    });

    if (response.generatedImages && response.generatedImages.length > 0) {
      const base64ImageBytes = response.generatedImages[0].image.imageBytes;
      return `data:image/png;base64,${base64ImageBytes}`;
    }
    return null;
  } catch (error) {
    console.error("Error generating image:", error);
    return null;
  }
};

/**
 * Gets a response from the AI assistant for a chat conversation.
 * @param history The conversation history.
 * @param newPrompt The new user prompt.
 * @returns The AI's text response.
 */
export const getAIAssistantResponse = async (history: GeminiContent[], newPrompt: string): Promise<string> => {
  try {
    const contents = [...history, { role: 'user', parts: [{ text: newPrompt }] }];
    
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: contents,
      config: {
        systemInstruction: "You are a helpful assistant for writing and refining AI prompts. Your name is Prompt Pal. Keep your answers concise and helpful."
      }
    });

    return response.text;
  } catch (error) {
    console.error("Error getting AI assistant response:", error);
    return "Sorry, I encountered an error. Please try again.";
  }
};

/**
 * Edits an image based on a text instruction.
 * @param base64ImageUrl The original image as a base64 data URL.
 * @param instruction The text instruction for editing.
 * @returns A new base64 encoded image string, or null on failure.
 */
export const editImage = async (base64ImageUrl: string, instruction: string): Promise<string | null> => {
  try {
    const match = base64ImageUrl.match(/^data:(image\/.+);base64,(.+)$/);
    if (!match) {
      throw new Error("Invalid image URL format. Must be a base64 data URL.");
    }
    const mimeType = match[1];
    const base64ImageData = match[2];

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: {
        parts: [
          {
            inlineData: {
              data: base64ImageData,
              mimeType: mimeType,
            },
          },
          {
            text: instruction,
          },
        ],
      },
      config: {
        responseModalities: [Modality.IMAGE],
      },
    });

    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        const newBase64Data = part.inlineData.data;
        const newMimeType = part.inlineData.mimeType;
        return `data:${newMimeType};base64,${newBase64Data}`;
      }
    }
    return null;
  } catch (error) {
    console.error("Error editing image:", error);
    return null;
  }
};

/**
 * Generates personalized prompt ideas based on user's existing prompts.
 * @param userPrompts A sample of the user's prompts.
 * @returns An array of new prompt suggestions.
 */
export const getDynamicInspirations = async (userPrompts: Prompt[]): Promise<Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>[]> => {
  if (userPrompts.length === 0) return [];

  // Take the 5 most recently updated prompts as a sample
  const samplePrompts = userPrompts
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5)
    .map(({ title, type, tags }) => ({ title, type, tags }));
  
  const promptForAI = `You are a creative assistant for a "Prompt Studio" app. A user has saved these prompts: ${JSON.stringify(samplePrompts, null, 2)}.
Based on their style and topics, generate 6 new, creative, and diverse prompt ideas they might like.
Provide a title, the full prompt content, a suitable type ('image', 'text', 'video', or 'music'), and an array of 3 relevant tags for each.
Return the response as a valid JSON array of objects.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: promptForAI,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING },
              content: { type: Type.STRING },
              type: { type: Type.STRING, enum: Object.values(PromptType) },
              tags: { type: Type.ARRAY, items: { type: Type.STRING } },
            },
            required: ['title', 'content', 'type', 'tags'],
          },
        },
      },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Error generating dynamic inspirations:", error);
    return [];
  }
};

/**
 * Fuses multiple images based on a text prompt.
 * @param base64Images An array of base64 encoded image data URLs.
 * @param prompt The text prompt for fusing the images.
 * @returns A new base64 encoded image string, or null on failure.
 */
export const fuseFaces = async (base64Images: string[], prompt: string): Promise<string | null> => {
  try {
    const imageParts = base64Images.map(imageUrl => {
      const match = imageUrl.match(/^data:(image\/.+);base64,(.+)$/);
      if (!match) {
        throw new Error(`Invalid image URL format: ${imageUrl.substring(0, 30)}...`);
      }
      const mimeType = match[1];
      const base64ImageData = match[2];
      return {
        inlineData: {
          data: base64ImageData,
          mimeType: mimeType,
        },
      };
    });

    const textPart = { text: prompt };

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: {
        parts: [...imageParts, textPart],
      },
      config: {
        responseModalities: [Modality.IMAGE],
      },
    });

    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        const newBase64Data = part.inlineData.data;
        const newMimeType = part.inlineData.mimeType;
        return `data:${newMimeType};base64,${newBase64Data}`;
      }
    }
    return null;

  } catch (error) {
    console.error("Error fusing faces:", error);
    return null;
  }
};


// --- Text Studio Functions ---

const handleTextGeneration = async (prompt: string): Promise<string> => {
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
        });
        return response.text;
    } catch (error) {
        console.error("Error in text generation:", error);
        throw new Error("Failed to communicate with the AI.");
    }
};

export const generateCreativeText = (prompt: string) => handleTextGeneration(prompt);
export const summarizeText = (text: string) => handleTextGeneration(`Summarize the following text concisely and accurately:\n\n---\n\n${text}`);
export const rephraseText = (text: string, tone: string) => handleTextGeneration(`Rephrase the following text in a ${tone} tone. Do not add any extra commentary, just provide the rephrased text:\n\n---\n\n${text}`);
export const translateText = (text: string, language: string) => handleTextGeneration(`Translate the following text to ${language}. Only provide the translation, nothing else:\n\n---\n\n${text}`);

// --- Music Studio Functions ---

/**
 * Generates music from a text prompt.
 * NOTE: This is a placeholder. A direct text-to-music model is not yet available in the public @google/genai SDK.
 * This function simulates an API call and will be ready for integration when a model becomes available.
 * @param prompt The text prompt for music generation.
 * @param durationInSeconds The desired duration of the music track.
 * @returns A URL to the generated audio file, or null on failure.
 */
export const generateMusic = async (prompt: string, durationInSeconds: number): Promise<string | null> => {
  console.log(`Music generation requested for prompt: "${prompt}" with duration: ${durationInSeconds}s.`);
  console.warn("Music generation model (e.g., Lyria) is not yet available via the public Gemini API. Returning null.");
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // In a real app, this would be an actual API call.
  // For now, we return null to indicate the feature is not yet implemented.
  return null;
};