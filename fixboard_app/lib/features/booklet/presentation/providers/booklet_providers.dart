import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/booklet_entities.dart';
import '../../domain/usecases/booklet_usecases.dart';
import '../../data/repositories/booklet_repository_impl.dart';
import '../../data/datasources/booklet_remote_datasource.dart';

final bookletRemoteDataSourceProvider = Provider((ref) => BookletRemoteDataSource());

final bookletRepositoryProvider = Provider((ref) {
  final remoteDataSource = ref.watch(bookletRemoteDataSourceProvider);
  return BookletRepositoryImpl(remoteDataSource: remoteDataSource);
});

final getChaptersProvider = Provider((ref) {
  final repository = ref.watch(bookletRepositoryProvider);
  return GetChapters(repository);
});

final chaptersProvider = FutureProvider<List<Chapter>>((ref) async {
  final getChapters = ref.watch(getChaptersProvider);
  return await getChapters();
});

final lessonsProvider = FutureProvider.family<List<Lesson>, String>((ref, chapterId) async {
  final repository = ref.watch(bookletRepositoryProvider);
  final getLessons = GetLessons(repository);
  return await getLessons(chapterId);
});
