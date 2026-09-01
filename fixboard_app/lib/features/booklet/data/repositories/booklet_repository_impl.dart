import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../domain/entities/booklet_entities.dart';
import '../domain/repositories/booklet_repository.dart';
import 'datasources/booklet_remote_datasource.dart';

class BookletRepositoryImpl implements BookletRepository {
  final BookletRemoteDataSource remoteDataSource;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  BookletRepositoryImpl({required this.remoteDataSource});

  @override
  Future<List<Chapter>> getChapters() async {
    return await remoteDataSource.getChapters();
  }

  @override
  Future<List<Lesson>> getLessons(String chapterId) async {
    return await remoteDataSource.getLessons(chapterId);
  }

  @override
  Future<bool> isChapterPurchased(String userId, String chapterId) async {
    final doc = await _firestore
        .collection('users')
        .doc(userId)
        .collection('purchases')
        .doc(chapterId)
        .get();
    return doc.exists;
  }

  @override
  Future<void> purchaseChapter(String userId, String chapterId) async {
    await _firestore
        .collection('users')
        .doc(userId)
        .collection('purchases')
        .doc(chapterId)
        .set({
      'purchaseDate': FieldValue.serverTimestamp(),
      'chapterId': chapterId,
    });
  }
}
