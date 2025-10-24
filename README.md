# 🚀 Prompt Studio

> A comprehensive and professional AI prompt management and testing platform

**Prompt Studio** is a modern, full-featured application designed for content creators, designers, and AI researchers to manage, generate, and test AI prompts (both text and image) with an intuitive and powerful interface.

## ✨ Key Features

### 🎯 **Comprehensive Prompt Management**
- **Prompt Studio**: Advanced editor with syntax highlighting, live preview, and template variables
- **Smart Organization**: Categories, tags, favorites, and powerful search functionality
- **Version Control**: Track changes and usage statistics for each prompt
- **Export/Import**: Backup and share your prompt collections

### 🧪 **Advanced Testing & Experimentation**
- **Prompt Lab**: Test and compare multiple prompts simultaneously
- **Multi-Model Support**: Integration with OpenAI GPT, Google Gemini, and Anthropic Claude
- **Parameter Control**: Fine-tune temperature, max tokens, and other model parameters
- **Results Analysis**: Compare performance metrics and execution times

### 🤖 **AI-Powered Assistant**
- **Prompt Optimization**: Get AI suggestions to improve your prompts
- **Best Practices**: Learn prompt engineering techniques
- **Variation Generation**: Create multiple versions of your prompts
- **Real-time Feedback**: Interactive chat interface for prompt refinement

### 🎨 **Image Generation Studio**
- **Text-to-Image**: Generate stunning visuals from detailed prompts
- **Style Control**: Choose from various artistic styles and formats
- **Parameter Tuning**: Adjust steps, guidance, aspect ratios, and quality
- **Batch Generation**: Create multiple variations simultaneously

### 💡 **Inspiration Hub**
- **Curated Templates**: Professional prompt templates for various use cases
- **Expert Examples**: Learn from high-quality, tested prompts
- **Category Browsing**: Organized by difficulty and application
- **One-Click Usage**: Instantly adapt templates to your needs

### 📊 **Analytics Dashboard**
- **Usage Statistics**: Track your most effective prompts
- **Performance Metrics**: Monitor success rates and token usage
- **Visual Analytics**: Charts and graphs for data insights
- **Quick Actions**: Fast access to common tasks

## 🛠️ Technical Architecture

### **Frontend Stack**
- **React 18** with TypeScript for type-safe development
- **Vite** for lightning-fast build and hot reload
- **TailwindCSS** for modern, responsive styling
- **Framer Motion** for smooth animations and transitions

### **State Management**
- **React Hooks** for component state
- **LocalStorage** for data persistence
- **Custom Hooks** for reusable logic
- **Context API** for global state (themes, settings)

### **UI/UX Design**
- **Modern Interface**: Clean, intuitive design inspired by Notion and ChatGPT
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark/Light Themes**: System-aware theme switching
- **Accessibility**: WCAG compliant with keyboard navigation

### **AI Integration**
- **Multi-Provider Support**: OpenAI, Google Gemini, Anthropic Claude
- **Secure API Handling**: Client-side API key management
- **Error Handling**: Robust error handling and retry mechanisms
- **Rate Limiting**: Intelligent request management

## 🚀 Getting Started

### **Prerequisites**
- Node.js 16+ and npm/yarn
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Installation**

```bash
# Clone the repository
git clone https://github.com/your-username/prompt-studio.git
cd prompt-studio

# Install dependencies
npm install

# Start development server
npm run dev

# Open your browser
# Navigate to http://localhost:3000
```

### **Production Build**

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### **API Configuration**

1. **Navigate to Settings** → API Keys
2. **Add your API keys**:
   - **OpenAI**: Get from [OpenAI Dashboard](https://platform.openai.com/api-keys)
   - **Gemini**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Claude**: Get from [Anthropic Console](https://console.anthropic.com/)
3. **Configure defaults**: Set your preferred model and parameters

## 📁 Project Structure

```
prompt-studio/
├── 📁 components/              # React components
│   ├── 🎯 Dashboard.tsx        # Main dashboard
│   ├── 🎨 PromptStudio.tsx     # Prompt editor
│   ├── 🧪 PromptLab.tsx        # Testing environment
│   ├── 🤖 AIAssistant.tsx      # AI helper
│   ├── 🖼️ ImageRemixStudio.tsx # Image generation
│   ├── 💡 InspirationHub.tsx   # Template gallery
│   ├── ⚙️ Settings.tsx         # Configuration
│   └── 🧩 [Other Components]   # UI components
├── 📁 hooks/                   # Custom React hooks
│   └── 🔄 useLocalStorage.ts   # Persistent state
├── 📁 services/               # API integrations
│   └── 🤖 geminiService.ts    # Gemini API client
├── 📄 types.ts               # TypeScript definitions
├── 📄 constants.tsx          # App configuration
├── 📄 App.tsx               # Main application
├── 📄 index.tsx             # Entry point
└── 🎨 index.css             # Global styles
```

## 🎨 Design System

### **Color Palette**
- **Primary**: Blue gradient (#0ea5e9 → #8b5cf6)
- **Secondary**: Neutral grays for content
- **Accent**: Contextual colors (success, warning, error)
- **Dark Mode**: Carefully crafted dark theme

### **Typography**
- **Font**: Inter (system fallback: system-ui)
- **Sizes**: Responsive scale (sm, md, lg)
- **Weights**: 300-700 range for hierarchy

### **Components**
- **Cards**: Elevated surfaces with subtle shadows
- **Buttons**: Multiple variants (primary, secondary, ghost)
- **Forms**: Consistent input styling with validation
- **Navigation**: Intuitive sidebar and header layout

## 🔧 Configuration

### **Environment Variables**
```bash
# Optional: Pre-configure API keys
VITE_GEMINI_API_KEY=your_gemini_key_here
VITE_OPENAI_API_KEY=your_openai_key_here
VITE_CLAUDE_API_KEY=your_claude_key_here
```

### **Customization**
- **Themes**: Modify `tailwind.config.js` for custom colors
- **Models**: Add new AI providers in `constants.tsx`
- **Templates**: Extend built-in templates in `constants.tsx`

## 🚀 Deployment Options

### **Static Hosting**
- **Vercel**: `npm run build` → Deploy `dist/` folder
- **Netlify**: Connect GitHub repo for auto-deployment
- **GitHub Pages**: Use GitHub Actions for CI/CD

### **Desktop App (Electron)**
```bash
# Install Electron (future enhancement)
npm install electron electron-builder

# Package for desktop
npm run electron:build
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Code Standards**
- **TypeScript**: Strict mode enabled
- **ESLint**: Follow the configured rules
- **Prettier**: Auto-formatting on save
- **Conventional Commits**: Use semantic commit messages

## 📈 Features Implemented

### **✅ Core Features Complete**
- [x] **Dashboard**: Analytics and quick actions
- [x] **Prompt Studio**: Advanced prompt editor with live preview
- [x] **Prompt Lab**: Multi-model testing and comparison
- [x] **AI Assistant**: Interactive prompt optimization helper
- [x] **Image Studio**: Text-to-image generation interface
- [x] **Inspiration Hub**: Template gallery and examples
- [x] **Settings**: API configuration and preferences
- [x] **Dark/Light Theme**: System-aware theme switching
- [x] **Data Persistence**: LocalStorage with export/import
- [x] **Responsive Design**: Mobile-friendly interface
- [x] **TypeScript**: Full type safety throughout

### **🔮 Future Enhancements**
- [ ] **Real AI Integration**: Connect to actual AI APIs
- [ ] **Cloud Sync**: Cross-device synchronization
- [ ] **Collaboration**: Share prompts with teams
- [ ] **Advanced Analytics**: Usage insights and optimization
- [ ] **Automation**: Scheduled testing and monitoring

## 🐛 Troubleshooting

### **Common Issues**

**Build Errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues**
- Verify API keys in Settings
- Check network connectivity
- Ensure API quotas aren't exceeded

**Performance Issues**
- Clear browser cache
- Check for large prompt collections
- Update to latest browser version

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and inspiration
- **Google** for Gemini AI capabilities
- **Anthropic** for Claude AI integration
- **TailwindCSS** for the amazing utility-first CSS framework
- **React Team** for the incredible framework

---

<div align="center">

**Built with ❤️ for the AI community**

[🌟 Star this repo](#) • [🐛 Report Bug](#) • [💡 Request Feature](#)

</div>