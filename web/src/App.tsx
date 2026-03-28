import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import MirrorPage from './pages/MirrorPage';
import SelfMirrorPage from './pages/SelfMirrorPage';
import DashboardPage from './pages/DashboardPage';
import SetupPage from './pages/SetupPage';
import AdminPage from './pages/AdminPage';
import './App.css';

function App() {
  const { t, i18n } = useTranslation();

  const toggleLanguage = () => {
    const next = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
  };

  return (
    <BrowserRouter>
      <nav className="zyj-nav">
        <div className="zyj-nav-brand">
          <span className="zyj-nav-logo">&#x9B54;</span>
          <span className="zyj-nav-title">{t('app_name')}</span>
        </div>
        <div className="zyj-nav-links">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'zyj-nav-link active' : 'zyj-nav-link'}>
            {t('mirror')}
          </NavLink>
          <NavLink to="/self-mirror" className={({ isActive }) => isActive ? 'zyj-nav-link active' : 'zyj-nav-link'}>
            {t('self_mirror')}
          </NavLink>
          <NavLink to="/setup" className={({ isActive }) => isActive ? 'zyj-nav-link active' : 'zyj-nav-link'}>
            {t('setup')}
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'zyj-nav-link active' : 'zyj-nav-link'}>
            Dashboard
          </NavLink>
          <NavLink to="/admin" className={({ isActive }) => isActive ? 'zyj-nav-link active' : 'zyj-nav-link'}>
            {t('admin')}
          </NavLink>
        </div>
        <button className="zyj-lang-toggle" onClick={toggleLanguage}>
          {i18n.language === 'zh' ? 'EN' : '中文'}
        </button>
      </nav>
      <main className="zyj-main">
        <Routes>
          <Route path="/" element={<MirrorPage />} />
          <Route path="/self-mirror" element={<SelfMirrorPage />} />
          <Route path="/setup" element={<SetupPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
