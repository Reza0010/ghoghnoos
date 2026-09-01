import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/datasources/ai_api_client.dart';

class AiAssistantState {
  final String rawLog;
  final bool isAnalyzing;
  final String analysisStep;
  final Map<String, dynamic>? report;
  final String? errorMessage;

  AiAssistantState({
    required this.rawLog,
    required this.isAnalyzing,
    required this.analysisStep,
    this.report,
    this.errorMessage,
  });

  factory AiAssistantState.initial() {
    return AiAssistantState(
      rawLog: '',
      isAnalyzing: false,
      analysisStep: '',
    );
  }

  AiAssistantState copyWith({
    String? rawLog,
    bool? isAnalyzing,
    String? analysisStep,
    Map<String, dynamic>? report,
    String? errorMessage,
  }) {
    return AiAssistantState(
      rawLog: rawLog ?? this.rawLog,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      analysisStep: analysisStep ?? this.analysisStep,
      report: report ?? this.report,
      errorMessage: errorMessage, // can be set to null
    );
  }
}

class AiAssistantNotifier extends StateNotifier<AiAssistantState> {
  final AiApiClient _apiClient;

  AiAssistantNotifier(this._apiClient) : super(AiAssistantState.initial());

  void setLog(String log) {
    state = state.copyWith(rawLog: log);
  }

  Future<void> runDiagnostics() async {
    if (state.rawLog.trim().isEmpty) {
      state = state.copyWith(errorMessage: 'لطفاً ابتدا لاگ دستگاه را وارد کنید.');
      return;
    }

    state = state.copyWith(
      isAnalyzing: true,
      analysisStep: 'در حال تجزیه ساختار فایل لاگ (Header Parsing)...',
      errorMessage: null,
      report: null,
    );

    // Step 1 animation
    await Future.delayed(const Duration(milliseconds: 600));
    state = state.copyWith(analysisStep: 'بررسی آدرس‌دهی و ماتریس تراشه‌های اسیک...');

    // Step 2 animation
    await Future.delayed(const Duration(milliseconds: 600));
    state = state.copyWith(analysisStep: 'کنترل سرعت فن‌ها و خوانش سنسورهای حرارتی...');

    // Step 3 animation
    await Future.delayed(const Duration(milliseconds: 600));
    state = state.copyWith(analysisStep: 'استعلام از پایگاه داده هوش مصنوعی و تولید توصیه تعمیراتی...');

    // Final response
    try {
      final res = await _apiClient.analyzeLog(state.rawLog);
      state = state.copyWith(
        isAnalyzing: false,
        analysisStep: '',
        report: res,
      );
    } catch (e) {
      state = state.copyWith(
        isAnalyzing: false,
        analysisStep: '',
        errorMessage: 'خطا در عیب‌یابی لاگ: $e',
      );
    }
  }

  void clear() {
    state = AiAssistantState.initial();
  }
}

// Global Providers for Dependency Injection
final aiApiClientProvider = Provider((ref) => AiApiClient());

final aiAssistantProvider = StateNotifierProvider<AiAssistantNotifier, AiAssistantState>((ref) {
  final apiClient = ref.watch(aiApiClientProvider);
  return AiAssistantNotifier(apiClient);
});
