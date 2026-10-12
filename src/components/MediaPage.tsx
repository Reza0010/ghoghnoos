import React, { useState } from 'react';
import {
  Image as ImageIcon,
  Video,
  FileCode,
  Music,
  Plus,
  Trash2,
  HardDrive,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

interface MediaAsset {
  id: number;
  path: string;
  filename: string;
  kind: 'photo' | 'video' | 'audio' | 'document';
  size: number;
  sha1: string;
  added_at: string;
  note: string;
}

interface MediaPageProps {
  assets: MediaAsset[];
  onAddMedia: (data: any) => Promise<void>;
  onDeleteMedia: (id: number) => Promise<void>;
}

export const MediaPage: React.FC<MediaPageProps> = ({
  assets,
  onAddMedia,
  onDeleteMedia
}) => {
  const [filterKind, setFilterKind] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  // Form
  const [filename, setFilename] = useState('');
  const [kind, setKind] = useState<'photo' | 'video' | 'audio' | 'document'>('photo');
  const [sizeMB, setSizeMB] = useState('2.5');
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filteredAssets = assets.filter(a => filterKind === 'all' || a.kind === filterKind);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filename.trim()) return;
    setIsSubmitting(true);
    try {
      const bytes = Math.round(parseFloat(sizeMB) * 1024 * 1024);
      await onAddMedia({
        filename,
        kind,
        size: bytes,
        note
      });
      setShowAddModal(false);
      setFilename('');
      setNote('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getIcon = (kind: string) => {
    switch (kind) {
      case 'photo': return <ImageIcon className="w-5 h-5 text-sky-400" />;
      case 'video': return <Video className="w-5 h-5 text-purple-400" />;
      case 'audio': return <Music className="w-5 h-5 text-emerald-400" />;
      default: return <FileCode className="w-5 h-5 text-amber-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Filter */}
      <div className="bg-[#121a23] border border-[#22303f] p-5 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-[#f7931a]" />
            <h2 className="text-base font-bold text-[#e8eef5]">
              کتابخانه رسانه و اسناد فنی (Bot API Media Library)
            </h2>
          </div>
          <p className="text-xs text-[#93a4b6] mt-1">
            اعتبارسنجی محدودیت‌های رسمی تلگرام: عکس تا ۱۰ مگابایت | ویدیو، صوت و اسناد تا ۵۰ مگابایت.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={filterKind}
            onChange={(e) => setFilterKind(e.target.value)}
            className="bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-1.5 text-xs text-[#e8eef5] focus:outline-none"
          >
            <option value="all">همه انواع فایل</option>
            <option value="photo">تصاویر (Photo)</option>
            <option value="video">ویدیوها (Video)</option>
            <option value="audio">فایل صوتی (Audio)</option>
            <option value="document">اسناد و شماتیک (Document)</option>
          </select>

          <button
            onClick={() => setShowAddModal(true)}
            className="bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold text-xs px-4 py-2 rounded-lg flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            ثبت فایل جدید
          </button>
        </div>
      </div>

      {/* Assets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredAssets.length > 0 ? (
          filteredAssets.map(asset => (
            <div
              key={asset.id}
              className="bg-[#121a23] border border-[#22303f] rounded-xl p-5 flex flex-col justify-between hover:border-[#f7931a]/40 transition-all space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 bg-[#17212d] rounded-lg border border-[#22303f]">
                    {getIcon(asset.kind)}
                  </div>
                  <span className="text-[10px] font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                    {formatSize(asset.size)}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-[#e8eef5] font-mono dir-ltr text-left line-clamp-1">
                  {asset.filename}
                </h3>
                <p className="text-xs text-[#93a4b6] mt-1.5 line-clamp-2">
                  {asset.note || 'بدون یادداشت'}
                </p>
              </div>

              <div className="pt-3 border-t border-[#22303f]/60 flex items-center justify-between text-xs text-[#64748b]">
                <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>سازگار با تلگرام</span>
                </div>

                <button
                  onClick={() => onDeleteMedia(asset.id)}
                  className="p-1.5 hover:bg-rose-500/20 text-[#64748b] hover:text-rose-400 rounded transition-colors"
                  title="حذف فایل"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 bg-[#121a23] border border-[#22303f] rounded-xl p-12 text-center text-xs text-[#64748b]">
            هیچ فایلی در این دسته‌بندی وجود ندارد.
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121a23] border border-[#22303f] rounded-2xl w-full max-w-md p-6 relative">
            <h3 className="text-base font-bold text-[#e8eef5] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-[#f7931a]" />
              ثبت و اعتبارسنجی رسانه جدید
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-[#93a4b6] mb-1.5">
                  نام فایل (همراه پسوند):
                </label>
                <input
                  type="text"
                  required
                  placeholder="antminer_s19_hashboard_schematic.pdf"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none focus:border-[#f7931a] font-mono text-left dir-ltr"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-[#93a4b6] mb-1.5">
                    نوع فایل:
                  </label>
                  <select
                    value={kind}
                    onChange={(e: any) => setKind(e.target.value)}
                    className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none"
                  >
                    <option value="photo">تصویر (تا ۱۰MB)</option>
                    <option value="video">ویدیو (تا ۵۰MB)</option>
                    <option value="audio">صوت (تا ۵۰MB)</option>
                    <option value="document">سند / دیتاشیت (تا ۵۰MB)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-[#93a4b6] mb-1.5">
                    حجم تخمینی (مگابایت):
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={sizeMB}
                    onChange={(e) => setSizeMB(e.target.value)}
                    className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3 py-2 text-[#e8eef5] focus:outline-none font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-[#93a4b6] mb-1.5">
                  توضیح یا یادداشت راهنما:
                </label>
                <input
                  type="text"
                  placeholder="مثال: نقشه تست‌پوینت‌های مدار تغذیه هیدرو"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  className="w-full bg-[#17212d] border border-[#22303f] rounded-lg px-3.5 py-2 text-[#e8eef5] focus:outline-none"
                />
              </div>

              <div className="pt-3 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-[#17212d] text-[#93a4b6] rounded-lg"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-[#f7931a] hover:bg-[#ffa633] text-[#0b0f14] font-bold rounded-lg disabled:opacity-50"
                >
                  {isSubmitting ? 'در حال ثبت...' : 'تأیید و ذخیره'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
