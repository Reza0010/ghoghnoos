package com.example.data.local

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface MinerDao {

    // ==================== Queries ====================

    @Query("SELECT * FROM miners ORDER BY lastSeenTimestamp DESC")
    fun getAllMiners(): Flow<List<MinerEntity>>

    @Query("SELECT * FROM miners ORDER BY lastSeenTimestamp DESC")
    suspend fun getAllMinersList(): List<MinerEntity>

    @Query("SELECT * FROM miners WHERE isOnline = 1 ORDER BY lastSeenTimestamp DESC")
    fun getOnlineMiners(): Flow<List<MinerEntity>>

    @Query("SELECT * FROM miners WHERE ipAddress = :ipAddress LIMIT 1")
    fun getMinerByIp(ipAddress: String): Flow<MinerEntity?>

    @Query("SELECT * FROM miners WHERE ipAddress = :ipAddress LIMIT 1")
    suspend fun getMinerByIpSync(ipAddress: String): MinerEntity?

    @Query("SELECT * FROM miners WHERE ipAddress IN (:ipAddresses)")
    suspend fun getMinersByIps(ipAddresses: List<String>): List<MinerEntity>

    @Query("SELECT * FROM miners WHERE model LIKE '%' || :query || '%' OR alias LIKE '%' || :query || '%' OR ipAddress LIKE '%' || :query || '%'")
    fun searchMiners(query: String): Flow<List<MinerEntity>>

    // ==================== Pagination ====================

    @Query("SELECT * FROM miners ORDER BY lastSeenTimestamp DESC LIMIT :limit OFFSET :offset")
    suspend fun getMinersPaged(limit: Int, offset: Int): List<MinerEntity>

    // ==================== Aggregates ====================

    @Query("SELECT COUNT(*) FROM miners")
    fun getTotalCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM miners WHERE isOnline = 1")
    fun getOnlineCount(): Flow<Int>

    @Query("SELECT SUM(hashrateGhs) FROM miners WHERE isOnline = 1")
    fun getTotalHashrate(): Flow<Double?>

    @Query("SELECT AVG(temperatureC) FROM miners WHERE isOnline = 1")
    fun getAverageTemperature(): Flow<Double?>

    // ==================== Insert/Update ====================

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate(miner: MinerEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(miners: List<MinerEntity>)

    /**
     * Upsert با حفظ alias - Transaction-safe
     */
    @Transaction
    suspend fun upsertPreservingAlias(miner: MinerEntity) {
        val existing = getMinerByIpSync(miner.ipAddress)
        val finalMiner = if (existing != null && existing.alias.isNotBlank()) {
            miner.copy(alias = existing.alias)
        } else {
            miner
        }
        insertOrUpdate(finalMiner)
    }

    /**
     * Upsert batch با حفظ alias
     */
    @Transaction
    suspend fun upsertAllPreservingAlias(miners: List<MinerEntity>) {
        if (miners.isEmpty()) return
        val ips = miners.map { it.ipAddress }
        val existingMap = getMinersByIps(ips).associateBy { it.ipAddress }

        val finalMiners = miners.map { miner ->
            val existing = existingMap[miner.ipAddress]
            if (existing != null && existing.alias.isNotBlank()) {
                miner.copy(alias = existing.alias)
            } else {
                miner
            }
        }
        insertAll(finalMiners)
    }

    // ==================== Update Specific Fields ====================

    @Query("UPDATE miners SET alias = :alias WHERE ipAddress = :ipAddress")
    suspend fun updateAlias(ipAddress: String, alias: String)

    @Query("UPDATE miners SET isOnline = :isOnline WHERE ipAddress = :ipAddress")
    suspend fun updateOnlineStatus(ipAddress: String, isOnline: Boolean)

    @Query("UPDATE miners SET lastSeenTimestamp = :timestamp WHERE ipAddress = :ipAddress")
    suspend fun updateLastSeen(ipAddress: String, timestamp: Long)

    // ==================== Delete ====================

    @Query("DELETE FROM miners WHERE ipAddress = :ipAddress")
    suspend fun deleteByIp(ipAddress: String)

    @Query("DELETE FROM miners WHERE ipAddress IN (:ipAddresses)")
    suspend fun deleteByIps(ipAddresses: List<String>)

    @Query("DELETE FROM miners")
    suspend fun clearAll()

    /**
     * حذف ماینرهایی که بیش از maxAgeMs میلی‌ثانیه دیده نشده‌اند
     */
    @Query("DELETE FROM miners WHERE lastSeenTimestamp < :cutoffTimestamp")
    suspend fun deleteStaleMiners(cutoffTimestamp: Long)

    // ==================== Maintenance ====================

    /**
     * آفلاین کردن همه ماینرها (قبل از اسکن جدید)
     */
    @Query("UPDATE miners SET isOnline = 0")
    suspend fun markAllOffline()
}
