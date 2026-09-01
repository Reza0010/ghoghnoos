import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/booklet_models.dart';

class BookletRemoteDataSource {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Future<List<ChapterModel>> getChapters() async {
    final snapshot = await _firestore.collection('chapters').orderBy('order').get();
    return snapshot.docs.map((doc) => ChapterModel.fromFirestore(doc.data(), doc.id)).toList();
  }

  Future<List<LessonModel>> getLessons(String chapterId) async {
    // Check if user has access to this chapter
    final chapterDoc = await _firestore.collection('chapters').doc(chapterId).get();
    final isFree = chapterDoc.data()?['isFree'] ?? false;

    if (!isFree) {
      final user = _auth.currentUser;
      if (user == null) throw Exception('برای دسترسی به این بخش باید وارد شوید.');

      final purchaseDoc = await _firestore
          .collection('users')
          .doc(user.uid)
          .collection('purchases')
          .doc(chapterId)
          .get();

      if (!purchaseDoc.exists) throw Exception('شما به این فصل دسترسی ندارید. لطفا ابتدا آن را خریداری کنید.');
    }

    final snapshot = await _firestore
        .collection('lessons')
        .where('chapterId', isEqualTo: chapterId)
        .orderBy('order')
        .get();
    return snapshot.docs.map((doc) => LessonModel.fromFirestore(doc.data(), doc.id)).toList();
  }
}
