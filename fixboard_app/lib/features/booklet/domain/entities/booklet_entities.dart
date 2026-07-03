class Chapter {
  final String id;
  final String title;
  final String description;
  final double price;
  final bool isFree;
  final int order;
  final List<String> lessonIds;

  Chapter({
    required this.id,
    required this.title,
    required this.description,
    required this.price,
    required this.isFree,
    required this.order,
    required this.lessonIds,
  });
}

class Lesson {
  final String id;
  final String chapterId;
  final String title;
  final String content; // Markdown content
  final List<String> imageUrls;
  final String? videoUrl;
  final int order;

  Lesson({
    required this.id,
    required this.chapterId,
    required this.title,
    required this.content,
    required this.imageUrls,
    this.videoUrl,
    required this.order,
  });
}

class Quiz {
  final String id;
  final String chapterId;
  final List<Question> questions;

  Quiz({
    required this.id,
    required this.chapterId,
    required this.questions,
  });
}

class Question {
  final String text;
  final List<String> options;
  final int correctOptionIndex;

  Question({
    required this.text,
    required this.options,
    required this.correctOptionIndex,
  });
}
