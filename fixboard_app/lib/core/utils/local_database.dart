import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class LocalDatabase {
  static final LocalDatabase _instance = LocalDatabase._internal();
  factory LocalDatabase() => _instance;
  LocalDatabase._internal();

  Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'fixboard.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE chapters(
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            price REAL,
            isFree INTEGER,
            order_index INTEGER
          )
        ''');
        await db.execute('''
          CREATE TABLE lessons(
            id TEXT PRIMARY KEY,
            chapterId TEXT,
            title TEXT,
            content TEXT,
            imageUrls TEXT,
            videoUrl TEXT,
            order_index INTEGER
          )
        ''');
        await db.execute('''
          CREATE TABLE purchases(
            id TEXT PRIMARY KEY,
            userId TEXT,
            chapterId TEXT,
            purchaseDate TEXT
          )
        ''');
      },
    );
  }
}
