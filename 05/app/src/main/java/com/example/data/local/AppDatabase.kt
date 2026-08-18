package com.example.data.local

import android.content.Context
import android.util.Log
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

/**
 * دیتابیس اصلی اپلیکیشن WhatsMiner Scanner
 */
@Database(
    entities = [MinerEntity::class],
    version = 6,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun minerDao(): MinerDao

    companion object {
        private const val TAG = "AppDatabase"
        private const val DB_NAME = "whatsminer_scanner_db"

        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    DB_NAME
                )
                    .fallbackToDestructiveMigration()
                    .setJournalMode(RoomDatabase.JournalMode.AUTOMATIC)
                    .build()

                INSTANCE = instance
                Log.i(TAG, "Database initialized: $DB_NAME")
                instance
            }
        }

        /**
         * برای تست‌های واحد: دیتابیس in-memory
         */
        fun getInMemoryDatabase(context: Context): AppDatabase {
            return Room.inMemoryDatabaseBuilder(
                context,
                AppDatabase::class.java
            )
                .allowMainThreadQueries()
                .build()
        }

        /**
         * حذف دیتابیس (برای debug یا reset)
         */
        fun destroyDatabase() {
            INSTANCE?.close()
            INSTANCE = null
        }
    }
}
