import { GoogleGenAI, Type, Modality } from "@google/genai";
import { Prompt, PromptType, GeminiContent } from "../types";

type GenAIOptions = {
  model?: string;
  // Pass-through config for the SDK; we keep it loosely typed for flexibility
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config?: any;
};

function getStored<T = string>(key: string, fallback?: T): T | undefined {
  try {
    if (typeof window !== 'undefined') {
      const v = window.localStorage.getItem(key);
      if (v != null) return JSON.parse(v);
    }
  } catch {}
  return fallback;
}

function getApiKey(): string | undefined {
  const local = getStored<string>('geminiApiKey');
  // IMPORTANT: use literal references so Vite replaces them at build time
  const envFromGemini: string | undefined = (process.env.GEMINI_API_KEY as unknown as string) || undefined;
  const envFromApiKey: string | undefined = (process.env.API_KEY as unknown as string) || undefined;
  const envKey = envFromGemini || envFromApiKey;
  return local || envKey;
}

function getDefaultModelFor(type: 'text' | 'image'): string {
  const local = getStored<string>(type === 'text' ? 'defaultTextModel' : 'defaultImageModel');
  if (local) return local;
  return type === 'text' ? 'gemini-2.5-flash' : 'imagen-4.0-generate-001';
}

function getDefaultTemperature(): number | undefined {
  const t = getStored<number>('defaultTemperature');
  return typeof t === 'number' ? t : undefined;
}

function getAIClient(): GoogleGenAI {
  const apiKey = getApiKey();
  if (!apiKey) {
    // Create a dummy client that will fail on call; callers handle gracefully
    return new GoogleGenAI({ apiKey: '' as unknown as string });
  }
  return new GoogleGenAI({ apiKey });
}

/**
 * Enhances a given prompt using AI.
 * @param prompt The user's prompt.
 * @param type The type of prompt.
 * @returns An object with improvements and suggested tags, or a specific error object on failure.
 */
// Update: Removed `| null` from return type as it's never null.
export const getPromptEnhancements = async (
  prompt: string,
  type: PromptType,
  options?: GenAIOptions
): Promise<{ improvements: string; tags: string[] }> => {
  try {
    const ai = getAIClient();
    const response = await ai.models.generateContent({
      model: options?.model || getDefaultModelFor('text'),
      contents: `Analyze and enhance the following prompt for a ${type} generation AI. Provide a better, more detailed version and suggest 3-5 relevant tags. Prompt: "${prompt}"`,
      config: {
        temperature: options?.config?.temperature ?? getDefaultTemperature(),
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
 * Generates an image from a text prompt.
 * @param prompt The text prompt for image generation.
 * @returns A base64 encoded image string, or null on failure.
 */
export const generateImage = async (prompt: string, options?: GenAIOptions): Promise<string | null> => {
  try {
    const ai = getAIClient();
    const response = await ai.models.generateImages({
      model: options?.model || getDefaultModelFor('image'),
      prompt: prompt,
      config: {
        numberOfImages: 1,
        outputMimeType: 'image/png',
        aspectRatio: '1:1',
        ...(options?.config || {}),
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
export const getAIAssistantResponse = async (
  history: GeminiContent[],
  newPrompt: string,
  options?: GenAIOptions
): Promise<string> => {
  try {
    const ai = getAIClient();
    const contents = [...history, { role: 'user', parts: [{ text: newPrompt }] }];
    
    const response = await ai.models.generateContent({
      model: options?.model || getDefaultModelFor('text'),
      contents: contents,
      config: {
        systemInstruction: "You are a helpful assistant for writing and refining AI prompts. Your name is Prompt Pal. Keep your answers concise and helpful.",
        temperature: options?.config?.temperature ?? getDefaultTemperature(),
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
export const editImage = async (base64ImageUrl: string, instruction: string, options?: GenAIOptions): Promise<string | null> => {
  try {
    const match = base64ImageUrl.match(/^data:(image\/.+);base64,(.+)$/);
    if (!match) {
      throw new Error("Invalid image URL format. Must be a base64 data URL.");
    }
    const mimeType = match[1];
    const base64ImageData = match[2];

    const ai = getAIClient();
    const response = await ai.models.generateContent({
      model: options?.model || 'gemini-2.5-flash-image',
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
        responseModalities: [Modality.IMAGE, Modality.TEXT],
        ...(options?.config || {}),
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
    const ai = getAIClient();
    const response = await ai.models.generateContent({
      model: getDefaultModelFor('text'),
      contents: promptForAI,
      config: {
        temperature: getDefaultTemperature(),
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
