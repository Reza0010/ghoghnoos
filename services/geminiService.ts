// services/geminiService.ts

import { GoogleGenAI, Part, Content } from "@google/genai";
import { UserProfile, Message } from "../types";
import { SYSTEM_PROMPT_TEMPLATE } from "../constants";

// 🚀 تغییر مهم در اینجا: استفاده از ساختار استاندارد Vite
// متغیرهای محیطی که با VITE_ شروع می‌شوند از این طریق در مرورگر قابل دسترسی هستند
const apiKey = import.meta.env.VITE_GEMINI_API_KEY; 

if (!apiKey) {
  // این خطا در محیط توسعه (Local) نمایش داده می‌شود، نه در محیط Netlify
  console.error("FATAL: VITE_GEMINI_API_KEY is missing!");
}

// اگر apiKey در Netlify تنظیم شده باشد، این مقدار معتبر خواهد بود
// اگر در زمان build نباشد (مثل محیط توسعه)، از 'dummy-key-for-build' استفاده می‌شود
const ai = new GoogleGenAI({ apiKey: apiKey || 'dummy-key-for-build' });

const modelName = 'gemini-2.5-flash';

// بقیه کد بدون تغییر باقی می مانند
export const generateWorkoutPlan = async (userProfile: UserProfile): Promise<string> => {
// ... بقیه کدهای تابع generateWorkoutPlan
// ...
// ...
  try {
    // Get Current Persian Date
    const date = new Intl.DateTimeFormat('fa-IR', { dateStyle: 'full' }).format(new Date());

    // 1. Prepare Text Profile (exclude raw base64 photo to avoid huge prompt)
    const profileString = Object.entries(userProfile)
      .filter(([key, value]) => {
         // Exclude the raw photo data from the text summary if it's an image
         if (key === 'photo' && value?.startsWith('data:image')) return false;
         return true;
      })
      .map(([key, value]) => `- ${key}: ${value}`)
      .join('\n');

    const systemInstruction = SYSTEM_PROMPT_TEMPLATE
      .replace('{{USER_PROFILE}}', profileString);

    // 2. Prepare Contents (Text + Image if exists)
    const userPromptText = `تاریخ امروز: ${date}\nلطفاً برنامه تمرینی اختصاصی من را با توجه به مشخصات و شرایطی که گفتم بنویس. کامل و دقیق باشد و تاریخ امروز را بالای برنامه ذکر کن.`;
    const parts: Part[] = [{ text: userPromptText }];

    // If there is a photo and it's base64 data, add it to parts
    if (userProfile.photo && userProfile.photo.startsWith('data:image')) {
      const matches = userProfile.photo.match(/^data:(.+);base64,(.+)$/);
      if (matches) {
        const mimeType = matches[1];
        const data = matches[2];
        parts.push({
          inlineData: {
            mimeType,
            data
          }
        });
      } else {
        parts.push({ text: "(User provided a photo but internal processing failed, proceed with text data)" });
      }
    }

    const response = await ai.models.generateContent({
      model: modelName,
      contents: [
        {
          role: 'user',
          parts: parts
        }
      ],
      config: {
        systemInstruction: systemInstruction,
        temperature: 0.7, // Creativity balance
      }
    });

    return response.text || "متاسفانه مشکلی در تولید برنامه پیش آمد. لطفا دوباره تلاش کنید.";
  } catch (error) {
    console.error("Error generating plan:", error);
    return "خطا در ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید یا بعداً تلاش کنید.";
  }
};

export const chatWithCoach = async (
  history: Message[], 
  userProfile: UserProfile, 
  newMessage: string
): Promise<string> => {
// ... بقیه کدهای تابع chatWithCoach
// ...
// ...
  try {
    const profileString = Object.entries(userProfile)
    .filter(([key, value]) => {
       if (key === 'photo' && value?.startsWith('data:image')) return false;
       return true;
    })
    .map(([key, value]) => `- ${key}: ${value}`)
    .join('\n');

    const systemInstruction = SYSTEM_PROMPT_TEMPLATE.replace('{{USER_PROFILE}}', profileString) 
      + "\n\nنکته مهم: الان برنامه صادر شده و کاربر سوالات تکمیلی دارد. کوتاه، مفید و در راستای برنامه داده شده جواب بده.";

    // Filter, Slice to last 10 messages for performance, and Map to Gemini format
    const contents: Content[] = history
      .filter(msg => !msg.text.startsWith('data:image') && msg.type !== 'card') // Filter out images and cards
      .slice(-10) // Keep only last 10 messages to avoid token limit and improve speed
      .map(msg => ({
        role: msg.sender === 'bot' ? 'model' : 'user',
        parts: [{ text: msg.text }]
      }));

    // Add the new message
    contents.push({
      role: 'user',
      parts: [{ text: newMessage }]
    });

    const response = await ai.models.generateContent({
      model: modelName,
      contents: contents,
      config: {
        systemInstruction: systemInstruction,
        temperature: 0.7,
      }
    });

    return response.text || "متوجه نشدم، لطفا دوباره بگو.";

  } catch (error) {
    console.error("Error in free chat:", error);
    return "مشکلی در پاسخگویی پیش آمده. لطفا دوباره تلاش کن.";
  }
};
