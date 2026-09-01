import '../entities/booklet_entities.dart';

abstract class BookletRepository {
  Future<List<Chapter>> getChapters();
  Future<List<Lesson>> getLessons(String chapterId);
  Future<bool> isChapterPurchased(String userId, String chapterId);
  Future<void> purchaseChapter(String userId, String chapterId);
}
