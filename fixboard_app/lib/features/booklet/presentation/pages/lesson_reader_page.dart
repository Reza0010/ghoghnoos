import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/booklet_providers.dart';

class LessonReaderPage extends ConsumerStatefulWidget {
  final String chapterId;
  const LessonReaderPage({super.key, required this.chapterId});

  @override
  ConsumerState<LessonReaderPage> createState() => _LessonReaderPageState();
}

class _LessonReaderPageState extends ConsumerState<LessonReaderPage> {
  double _fontSize = 18.0;
  bool _isDarkMode = false;
  late PageController _pageController;
  int _initialPage = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _fontSize = prefs.getDouble('fontSize') ?? 18.0;
      _isDarkMode = prefs.getBool('isDarkMode') ?? false;
      _initialPage = prefs.getInt('lastPage_${widget.chapterId}') ?? 0;
    });

    // Jump to last saved page after first build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_pageController.hasClients) {
        _pageController.jumpToPage(_initialPage);
      }
    });
  }

  Future<void> _savePreferences() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('fontSize', _fontSize);
    await prefs.setBool('isDarkMode', _isDarkMode);
    if (_pageController.hasClients) {
      await prefs.setInt('lastPage_${widget.chapterId}', _pageController.page!.round());
    }
  }

  @override
  Widget build(BuildContext context) {
    final lessonsAsync = ref.watch(lessonsProvider(widget.chapterId));

    return Theme(
      data: _isDarkMode ? ThemeData.dark() : ThemeData.light(),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('آموزش Fixboard'),
          actions: [
            IconButton(
              icon: const Icon(Icons.text_fields),
              onPressed: () {
                setState(() {
                  _fontSize = _fontSize >= 28 ? 16 : _fontSize + 2;
                });
                _savePreferences();
              },
            ),
            IconButton(
              icon: Icon(_isDarkMode ? Icons.light_mode : Icons.dark_mode),
              onPressed: () {
                setState(() {
                  _isDarkMode = !_isDarkMode;
                });
                _savePreferences();
              },
            ),
          ],
        ),
        body: lessonsAsync.when(
          data: (lessons) => PageView.builder(
            controller: _pageController,
            onPageChanged: (page) => _savePreferences(),
            itemCount: lessons.length,
            itemBuilder: (context, index) {
              final lesson = lessons[index];
              return Padding(
                padding: const EdgeInsets.all(20.0),
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        lesson.title,
                        style: TextStyle(
                          fontSize: _fontSize + 6,
                          fontWeight: FontWeight.bold,
                          color: _isDarkMode ? Colors.amber : Colors.blue.shade900,
                        ),
                        textAlign: TextAlign.right,
                        textDirection: TextDirection.rtl,
                      ),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 16),
                      MarkdownBody(
                        data: lesson.content,
                        styleSheet: MarkdownStyleSheet(
                          p: TextStyle(fontSize: _fontSize, height: 1.6),
                          h1: TextStyle(fontSize: _fontSize + 8, fontWeight: FontWeight.bold),
                          h2: TextStyle(fontSize: _fontSize + 4, fontWeight: FontWeight.bold),
                        ),
                        selectable: true,
                        onTapLink: (text, href, title) {
                          // Handle links
                        },
                        imageBuilder: (uri, title, alt) {
                           return GestureDetector(
                             onTap: () => _showImageZoom(context, uri.toString()),
                             child: ClipRRect(
                               borderRadius: BorderRadius.circular(12),
                               child: Image.network(uri.toString()),
                             ),
                           );
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, stack) => Center(child: Text('خطا در بارگذاری: $err')),
        ),
      ),
    );
  }

  void _showImageZoom(BuildContext context, String imageUrl) {
    showDialog(
      context: context,
      builder: (context) => Dialog.fullscreen(
        child: Stack(
          children: [
            InteractiveViewer(
              minScale: 0.5,
              maxScale: 4.0,
              child: Center(
                child: Image.network(imageUrl),
              ),
            ),
            Positioned(
              top: 40,
              right: 20,
              child: CircleAvatar(
                backgroundColor: Colors.black54,
                child: IconButton(
                  icon: const Icon(Icons.close, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
}
