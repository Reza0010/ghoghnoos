import { writeTextFile, readTextFile } from '@tauri-apps/api/fs';
import { appDir } from '@tauri-apps/api/path';

const BACKUP_FILE = 'prompt-studio-backup.json';

export async function getAppStoragePath() {
  return await appDir();
}

export async function saveBackup(data: any) {
  const dir = await getAppStoragePath();
  const filePath = `${dir}${BACKUP_FILE}`;
  await writeTextFile({ path: filePath, contents: JSON.stringify(data, null, 2) });
}

export async function loadBackup(): Promise<any | null> {
  try {
    const dir = await getAppStoragePath();
    const filePath = `${dir}${BACKUP_FILE}`;
    const txt = await readTextFile(filePath);
    return JSON.parse(txt);
  } catch (e) {
    return null;
  }
}

let backupIntervalId: number | null = null;

export function setupAutoBackup(getData: () => any, intervalMs = 30_000) {
  if (backupIntervalId) window.clearInterval(backupIntervalId);
  backupIntervalId = window.setInterval(async () => {
    try {
      const data = getData();
      await saveBackup(data);
    } catch (e) {
      console.error('Auto backup failed', e);
    }
  }, intervalMs);

  window.addEventListener('beforeunload', async () => {
    try {
      const data = getData();
      await saveBackup(data);
    } catch (e) {
      console.error('Backup on close failed', e);
    }
  });
}

export function stopAutoBackup() {
  if (backupIntervalId) {
    window.clearInterval(backupIntervalId);
    backupIntervalId = null;
  }
}
