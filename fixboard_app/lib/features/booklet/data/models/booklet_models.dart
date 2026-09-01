import '../entities/booklet_entities.dart';

class ChapterModel extends Chapter {
  ChapterModel({
    required super.id,
    required super.title,
    required super.description,
    required super.price,
    required super.isFree,
    required super.order,
    required super.lessonIds,
  });

  factory ChapterModel.fromFirestore(Map<String, dynamic> data, String id) {
    return ChapterModel(
      id: id,
      title: data['title'] ?? '',
      description: data['description'] ?? '',
      price: (data['price'] ?? 0).toDouble(),
      isFree: data['isFree'] ?? false,
      order: data['order'] ?? 0,
      lessonIds: List<String>.from(data['lessonIds'] ?? []),
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'title': title,
      'description': description,
      'price': price,
      'isFree': isFree,
      'order': order,
      'lessonIds': lessonIds,
    };
  }
}

class LessonModel extends Lesson {
  LessonModel({
    required super.id,
    required super.chapterId,
    required super.title,
    required super.content,
    required super.imageUrls,
    super.videoUrl,
    required super.order,
  });

  factory LessonModel.fromFirestore(Map<String, dynamic> data, String id) {
    return LessonModel(
      id: id,
      chapterId: data['chapterId'] ?? '',
      title: data['title'] ?? '',
      content: data['content'] ?? '',
      imageUrls: List<String>.from(data['imageUrls'] ?? []),
      videoUrl: data['videoUrl'],
      order: data['order'] ?? 0,
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'chapterId': chapterId,
      'title': title,
      'content': content,
      'imageUrls': imageUrls,
      'videoUrl': videoUrl,
      'order': order,
    };
  }
}
