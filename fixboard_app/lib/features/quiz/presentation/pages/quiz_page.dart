import 'package:flutter/material.dart';
import '../../domain/entities/booklet_entities.dart';

class QuizPage extends StatefulWidget {
  final Quiz quiz;
  const QuizPage({super.key, required this.quiz});

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  int _currentQuestionIndex = 0;
  int _score = 0;
  bool _showResult = false;
  int? _selectedOptionIndex;

  @override
  Widget build(BuildContext context) {
    if (_showResult) {
      return _buildResult();
    }

    final question = widget.quiz.questions[_currentQuestionIndex];

    return Scaffold(
      appBar: AppBar(title: const Text('آزمون فصل')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            LinearProgressIndicator(
              value: (_currentQuestionIndex + 1) / widget.quiz.questions.length,
              backgroundColor: Colors.grey.shade200,
              color: Colors.blue,
            ),
            const SizedBox(height: 32),
            Text(
              'سوال ${(_currentQuestionIndex + 1)} از ${widget.quiz.questions.length}',
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Text(
              question.text,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.right,
              textDirection: TextDirection.rtl,
            ),
            const SizedBox(height: 32),
            ...List.generate(
              question.options.length,
              (index) => _buildOption(index, question.options[index]),
            ),
            const Spacer(),
            ElevatedButton(
              onPressed: _selectedOptionIndex == null ? null : _nextQuestion,
              child: Text(_currentQuestionIndex == widget.quiz.questions.length - 1 ? 'مشاهده نتیجه' : 'سوال بعدی'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOption(int index, String text) {
    bool isSelected = _selectedOptionIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedOptionIndex = index),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue.shade50 : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? Colors.blue : Colors.grey.shade300, width: 2),
        ),
        child: Row(
          children: [
            const Spacer(),
            Text(text, style: const TextStyle(fontSize: 18), textDirection: TextDirection.rtl),
            const SizedBox(width: 16),
            Icon(isSelected ? Icons.check_circle : Icons.circle_outlined, color: isSelected ? Colors.blue : Colors.grey),
          ],
        ),
      ),
    );
  }

  void _nextQuestion() {
    if (_selectedOptionIndex == widget.quiz.questions[_currentQuestionIndex].correctOptionIndex) {
      _score++;
    }

    if (_currentQuestionIndex < widget.quiz.questions.length - 1) {
      setState(() {
        _currentQuestionIndex++;
        _selectedOptionIndex = null;
      });
    } else {
      setState(() => _showResult = true);
    }
  }

  Widget _buildResult() {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.emoji_events, size: 100, color: Colors.amber),
            const SizedBox(height: 24),
            const Text('پایان آزمون', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Text(
              'امتیاز شما: $_score از ${widget.quiz.questions.length}',
              style: const TextStyle(fontSize: 22, color: Colors.blue),
            ),
            const SizedBox(height: 48),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('بازگشت به برنامه'),
            ),
          ],
        ),
      ),
    );
  }
}
