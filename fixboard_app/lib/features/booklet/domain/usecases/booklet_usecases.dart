import '../entities/booklet_entities.dart';
import '../repositories/booklet_repository.dart';

class GetChapters {
  final BookletRepository repository;
  GetChapters(this.repository);

  Future<List<Chapter>> call() async {
    return await repository.getChapters();
  }
}

class GetLessons {
  final BookletRepository repository;
  GetLessons(this.repository);

  Future<List<Lesson>> call(String chapterId) async {
    return await repository.getLessons(chapterId);
  }
}

class CheckPurchase {
  final BookletRepository repository;
  CheckPurchase(this.repository);

  Future<bool> call(String userId, String chapterId) async {
    return await repository.isChapterPurchased(userId, chapterId);
  }
}
