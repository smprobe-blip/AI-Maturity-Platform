/**
 * PublicChrome — шапка и подвал в стиле лендинга «Аудит»
 * для публичного флоу оценки ИИ-зрелости.
 * Стиль: бумага #f4f4f1 / чернила #15181b / акцент #0d6b4f, IBM Plex.
 */
import type { ReactNode } from 'react';
import '@/styles/public-theme.css';

const SITE = 'https://netbrainpower.ru';

export function PublicChrome({ children }: { children: ReactNode }) {
  return (
    <div className="nbp-pub min-h-screen flex flex-col">
      <header className="nbp-header">
        <a className="nbp-logo" href={SITE}>
          NetBrain<em>Power</em>
        </a>
        <nav className="nbp-nav">
          <a href={SITE + '/#method'}>О методике</a>
          <a href="/">Оценка</a>
          <a href={SITE + '/#contacts'}>Контакты</a>
        </nav>
        <span className="nbp-pill">апробировано в федеральном дискаунтере (сеть 500+ магазинов)</span>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="nbp-footer">
        <span>© 2026 NetBrainPower</span>
        <span>Методика разработана в рамках магистерской диссертации РАНХиГС</span>
      </footer>
    </div>
  );
}
