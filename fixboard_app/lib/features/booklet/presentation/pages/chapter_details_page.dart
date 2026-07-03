import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/booklet_entities.dart';
import '../providers/booklet_providers.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../../../auth/presentation/pages/login_page.dart';
import 'lesson_reader_page.dart';

class ChapterDetailsPage extends ConsumerWidget {
  final Chapter chapter;

  const ChapterDetailsPage({super.key, required this.chapter});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(title: Text(chapter.title)),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Hero(
              tag: 'chapter-${chapter.id}',
              child: const Icon(Icons.menu_book, size: 120, color: Colors.blue),
            ),
            const SizedBox(height: 32),
            Text(
              chapter.title,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
              textDirection: TextDirection.rtl,
            ),
            const SizedBox(height: 16),
            Text(
              chapter.description,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge,
              textDirection: TextDirection.rtl,
            ),
            const Spacer(),
            if (!chapter.isFree)
              _buildPriceInfo(chapter.price),
            const SizedBox(height: 24),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () => _handleAction(context, ref, authState.value),
              child: Text(
                chapter.isFree ? 'مطالعه رایگان' : 'خرید و باز کردن فصل',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceInfo(double price) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('تومان', style: TextStyle(fontSize: 16, color: Colors.green)),
          const SizedBox(width: 8),
          Text(
            price.toStringAsFixed(0),
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.green),
          ),
          const SizedBox(width: 8),
          const Text('قیمت:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  void _handleAction(BuildContext context, WidgetRef ref, dynamic user) async {
    if (chapter.isFree) {
      _navigateToReader(context);
      return;
    }

    if (user == null) {
      _showLoginPrompt(context);
      return;
    }

    // Check if already purchased
    final repository = ref.read(bookletRepositoryProvider);
    final isPurchased = await repository.isChapterPurchased(user.uid, chapter.id);

    if (isPurchased) {
      _navigateToReader(context);
    } else {
      _showPurchaseDialog(context, ref, user.uid);
    }
  }

  void _navigateToReader(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => LessonReaderPage(chapterId: chapter.id)),
    );
  }

  void _showLoginPrompt(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('نیاز به ورود', textDirection: TextDirection.rtl),
        content: const Text('برای خرید این فصل ابتدا باید وارد حساب کاربری خود شوید.', textDirection: TextDirection.rtl),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('انصراف')),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (context) => const LoginPage()));
            },
            child: const Text('ورود / ثبت نام'),
          ),
        ],
      ),
    );
  }

  void _showPurchaseDialog(BuildContext context, WidgetRef ref, String userId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تایید خرید', textDirection: TextDirection.rtl),
        content: Text('آیا مایل به خرید "${chapter.title}" هستید؟', textDirection: TextDirection.rtl),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('خرید از درگاه بانکی')),
          TextButton(
            onPressed: () async {
              // Simulated purchase
              await ref.read(bookletRepositoryProvider).purchaseChapter(userId, chapter.id);
              if (context.mounted) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('خرید با موفقیت انجام شد')));
                _navigateToReader(context);
              }
            },
            child: const Text('خرید آزمایشی'),
          ),
        ],
      ),
    );
  }
}
