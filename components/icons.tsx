import React from 'react';

type IconProps = React.SVGProps<SVGSVGElement> & {
  className?: string;
};

const defaultProps: IconProps = {
  xmlns: "http://www.w3.org/2000/svg",
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const Sun: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m4.93 17.66 1.41-1.41"/><path d="m17.66 4.93 1.41-1.41"/></svg>;
export const Moon: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>;
export const Plus: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M5 12h14"/><path d="M12 5v14"/></svg>;
export const Search: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>;
export const Star: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>;
export const Edit: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>;
export const Trash: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>;
export const Wand2: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="m12 3-1.5 1.5 4 4 1.5-1.5-4-4Z"/><path d="m3 12 1.5-1.5 4 4-1.5 1.5-4-4Z"/><path d="M21 12a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h3"/><path d="M21 21a1 1 0 0 0-1-1h-3a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h3.5a1 1 0 0 0 1-1z"/></svg>;
export const Copy: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>;
export const Bot: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>;
export const Send: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>;
export const Download: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>;
export const Upload: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>;
export const X: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>;
export const Sparkles: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="m12 3-1.9 1.9-1.9-1.9-1.9 1.9-1.9-1.9L2.5 5l1.9 1.9-1.9 1.9 1.9 1.9 1.9-1.9 1.9 1.9 1.9-1.9 1.9 1.9-1.9 1.9L12 21l1.9-1.9 1.9 1.9 1.9-1.9 1.9 1.9 1.9-1.9 1.9 1.9-1.9-1.9 1.9-1.9-1.9-1.9-1.9 1.9-1.9-1.9Z"/></svg>;
export const LayoutDashboard: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>;
export const Folders: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M20 17a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3.9a2 2 0 0 1-1.69-.9l-.81-1.2a2 2 0 0 0-1.67-.9H8a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2Z"/><path d="M2 8h17a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h5.17A2 2 0 0 1 8.83 3l1.06 1.6A2 2 0 0 0 11.56 5H13"/></svg>;
export const Image: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>;
export const FileText: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>;
export const Video: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.934a.5.5 0 0 0-.777-.416L16 11"/><rect x="2" y="7" width="14" height="10" rx="2" ry="2"/></svg>;
export const Music: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>;
export const Settings: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 0 2l-.15.08a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1 0-2l.15.08a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>;
export const Beaker: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M4.5 3h15"/><path d="M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3"/><path d="M6 14h12"/></svg>;
export const ArrowRight: React.FC<IconProps> = (props) => <svg {...defaultProps} {...props}><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>;
