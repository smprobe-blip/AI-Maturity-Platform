import { useState } from 'react';
import { HelpCircle } from 'lucide-react';

export interface QuestionHintData {
  id?: string;
  title?: string;
  tooltip: string;
  why_important: string;
  levels: Record<string, string>;
}

export function QuestionHint({ hint }: { hint?: QuestionHintData }) {
  const [open, setOpen] = useState(false);
  if (!hint) return null;

  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setOpen(!open);
        }}
        className="text-[#0d6b4f] hover:text-[#0a3d2e] transition-colors"
        aria-label="Показать подсказку"
      >
        <HelpCircle size={15} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40 cursor-default" onClick={() => setOpen(false)} />
          <div className="absolute z-50 top-6 sm:top-0 left-1/2 -translate-x-1/2 sm:left-full sm:translate-x-0 sm:ml-4 w-[min(39rem,92vw)] sm:w-[39rem] bg-white border border-[#dcded6] rounded-md shadow-xl p-4 text-left font-normal">
            <div className="text-sm font-bold text-gray-900 mb-2">{hint.title}</div>

            <div className="mb-2">
              <div className="text-xs font-semibold text-[#0a5640] mb-0.5">Теория</div>
              <p className="text-xs text-gray-700 leading-relaxed">{hint.tooltip}</p>
            </div>

            <div className="mb-3">
              <div className="text-xs font-semibold text-[#0a5640] mb-0.5">Почему это важно</div>
              <p className="text-xs text-gray-700 leading-relaxed">{hint.why_important}</p>
            </div>

            <div>
              <div className="text-xs font-semibold text-[#0a5640] mb-1">Уровни зрелости</div>
              <div className="space-y-1">
                {[1, 2, 3, 4, 5].map((lvl) => (
                  <div key={lvl} className="flex gap-2 items-start">
                    <span className="shrink-0 w-4 h-4 rounded bg-[#e6efe9] text-[#0a5640] text-[10px] font-bold flex items-center justify-center">
                      {lvl}
                    </span>
                    <span className="text-[11px] text-gray-600 leading-snug">
                      {hint.levels ? hint.levels[String(lvl)] : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </span>
  );
}
